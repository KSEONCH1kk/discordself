"""Полная поддержка Voice для Discord"""

from typing import Optional, Dict, Any, TYPE_CHECKING, Union, Callable
import asyncio
import logging
import socket
import struct
import time

logger = logging.getLogger(__name__)

try:
    from nacl.secret import SecretBox
    try:
        from nacl.secret import Aead
        AEAD_AVAILABLE = True
    except ImportError:
        AEAD_AVAILABLE = False
        logger.warning("PyNaCl Aead not available. Some encryption modes may not work.")
    NACL_AVAILABLE = True
except ImportError:
    NACL_AVAILABLE = False
    AEAD_AVAILABLE = False
    logger.warning("PyNaCl not available. Voice encryption will not work. Install with: pip install pynacl")

if TYPE_CHECKING:
    from .client import Client
    from .models import Guild, Channel, User
    from .audio_source import AudioSource

# Попробовать загрузить opus.dll ПЕРЕД импортом opuslib
import os
import sys

OPUS_AVAILABLE = False
opus_dll_path = None

# Пути для поиска opus.dll
possible_paths = [
    'opus.dll',
]

for path in possible_paths:
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path):
        opus_dll_path = abs_path
        break

if opus_dll_path:
    try:
        # Загрузить DLL напрямую через ctypes ПЕРЕД импортом opuslib
        import ctypes
        # Добавить директорию с DLL в PATH для Windows
        dll_dir = os.path.dirname(opus_dll_path)
        if sys.platform == 'win32':
            # Добавить в начало PATH, чтобы Windows нашел DLL первым
            current_path = os.environ.get('PATH', '')
            os.environ['PATH'] = dll_dir + os.pathsep + current_path
        
        # Загрузить DLL напрямую через ctypes
        try:
            opus_dll = ctypes.CDLL(opus_dll_path)
        except OSError as e:
            logger.warning(f"⚠️ Could not load opus.dll directly: {e}")
            logger.warning("   DLL may be missing dependencies or wrong architecture")
    except Exception as e:
        logger.warning(f"⚠️ Error preparing opus.dll: {e}")

# Теперь попробовать импортировать opuslib
try:
    import opuslib
    
    # Если opuslib имеет функцию load_opus, использовать её
    if opus_dll_path and hasattr(opuslib, 'load_opus'):
        try:
            opuslib.load_opus(opus_dll_path)
        except Exception as e:
            logger.warning(f"⚠️ opuslib.load_opus failed: {e}")
    
    # Проверить, работает ли opuslib
    try:
        # Попробовать создать тестовый encoder
        test_encoder = opuslib.Encoder(48000, 2, opuslib.APPLICATION_AUDIO)
        del test_encoder
        OPUS_AVAILABLE = True
    except Exception as e:
        OPUS_AVAILABLE = False
        logger.error(f"❌ Opus library found but not working: {e}")
        logger.error(f"   DLL path: {opus_dll_path}")
        logger.error("   Make sure opus.dll matches your Python architecture (32/64 bit)")
        logger.error("   And that all DLL dependencies are available")
    
except (ImportError, Exception) as e:
    OPUS_AVAILABLE = False
    logger.warning(f"opuslib not available. Audio encoding will not work. Error: {e}")
    if opus_dll_path:
        logger.warning(f"   Found opus.dll at: {opus_dll_path}")
        logger.warning("   But opuslib cannot load it. Try:")
        logger.warning("   1. Make sure opus.dll matches your Python architecture (32/64 bit)")
        logger.warning("   2. Install opuslib: pip install opuslib")
        logger.warning("   3. Check if opus.dll has all required dependencies")
        logger.warning("   4. Try placing opus.dll in the same directory as your script")

from .voice_gateway import VoiceGatewayClient
from .audio_source import AudioSource, PCMAudioSource, OpusAudioSource, SilenceSource
from .models import VoiceState  # VoiceState теперь в models.py


# VoiceState удален, теперь импортируется из models


class VoiceClient:
    """Полнофункциональный клиент для голосового подключения"""
    
    def __init__(self, client: 'Client', channel: 'Channel'):
        self.client: 'Client' = client
        self.channel: 'Channel' = channel
        self.guild: Optional['Guild'] = channel.guild
        self.voice_gateway: Optional[VoiceGatewayClient] = None
        self.udp_socket: Optional[socket.socket] = None
        self.endpoint: Optional[str] = None
        self.token: Optional[str] = None
        self.session_id: Optional[str] = None
        self.connected: bool = False
        self.ready: bool = False
        self.playing: bool = False
        self.paused: bool = False
        self.volume: float = 1.0
        
        # Аудио
        self.audio_source: Optional['AudioSource'] = None
        self.audio_task: Optional[asyncio.Task] = None
        self.encoder = None
        self.secret_key: Optional[bytes] = None
        self.ssrc: Optional[int] = None
        self.sequence: int = 0
        self.timestamp: int = 0
        
        # UDP
        self.udp_ip: Optional[str] = None
        self.udp_port: Optional[int] = None
        self.local_ip: Optional[str] = None
        self.local_port: Optional[int] = None
        
        # Режим шифрования
        self.encryption_mode: Optional[str] = None
        self._incr_nonce: int = 0  # Для режимов с инкрементирующимся nonce
        
        # Флаг для предотвращения двойного вызова _setup_udp
        self._udp_setup_in_progress: bool = False
    
    async def connect(self, *, reconnect: bool = True, timeout: float = 60.0, self_deaf: bool = False, self_mute: bool = False) -> None:
        """Подключиться к голосовому каналу"""
        if not self.guild:
            raise RuntimeError("Cannot connect to voice channel: not a guild channel")
        
        if not self.client.http:
            raise RuntimeError("HTTP client not initialized")
        
        if not self.client.user:
            raise RuntimeError("Client user not initialized")
        
        # Сохранить в voice_clients
        if self.guild:
            self.client.voice_clients[self.guild.id] = self
        
        # Установить voice state через основной Gateway
        await self._update_voice_state(self.channel.id, self_deaf, self_mute)
        
        # Ждать VOICE_SERVER_UPDATE и VOICE_STATE_UPDATE события
        # События будут обработаны в Client._on_voice_server_update и _on_voice_state_update
        # Дать время на получение событий
        for i in range(100):  # Ждать до 10 секунд
            if self.endpoint and self.token and self.session_id:
                break
            await asyncio.sleep(0.1)
        
        # Подключиться к Voice Gateway только после получения всех данных
        if not (self.endpoint and self.token and self.session_id):
            logger.error(f"❌ Voice server info not received: endpoint={bool(self.endpoint)}, token={bool(self.token)}, session_id={bool(self.session_id)}")
            raise RuntimeError("Failed to receive voice server information")
        
        # Убедиться, что endpoint не содержит wss://
        if self.endpoint.startswith('wss://'):
            self.endpoint = self.endpoint[6:]
        
        await self._connect_voice_gateway()
        
        # Использовать poll_event для синхронного handshake (как в discord.py)
        await self._handshake_voice_gateway()
        
        self.connected = True
    
    async def _update_voice_state(self, channel_id: Optional[int], self_deaf: bool, self_mute: bool):
        """Обновить voice state через Gateway"""
        # Отправить VOICE_STATE_UPDATE через основной Gateway
        if self.client.shard_manager and self.client.shard_manager.shards:
            shard = self.client.shard_manager.shards[0]
            if shard.gateway:
                payload = {
                    "op": 4,  # VOICE_STATE_UPDATE
                    "d": {
                        "guild_id": str(self.guild.id),
                        "channel_id": str(channel_id) if channel_id else None,
                        "self_deaf": self_deaf,
                        "self_mute": self_mute
                    }
                }
                await shard.gateway.send(payload)
            else:
                logger.error("❌ Gateway is None, cannot send VOICE_STATE_UPDATE")
        else:
            logger.error("❌ Shard manager or shards not available, cannot send VOICE_STATE_UPDATE")
    
    async def _connect_voice_gateway(self):
        """Подключиться к Voice Gateway"""
        if not self.endpoint or not self.token or not self.session_id:
            raise RuntimeError(f"Missing voice server information: endpoint={bool(self.endpoint)}, token={bool(self.token)}, session_id={bool(self.session_id)}")
        
        # Если уже подключен, отключиться
        if self.voice_gateway:
            logger.warning("Voice Gateway already exists, disconnecting...")
            try:
                await self.voice_gateway.disconnect()
            except:
                pass
            self.voice_gateway = None
        
        self.voice_gateway = VoiceGatewayClient(
            self.endpoint,
            self.token,
            self.session_id,
            self.guild.id,
            self.client.user.id
        )
        
        # Установить callbacks (для совместимости, но используем poll_event для handshake)
        self.voice_gateway.on_ready = self._on_voice_ready
        self.voice_gateway.on_session_description = self._on_session_description
        
        await self.voice_gateway.connect()
    
    async def _handshake_voice_gateway(self):
        """Выполнить handshake с Voice Gateway (как в discord.py)"""
        # Ждать READY (получение IP и порта)
        while not self.voice_gateway.ip:
            event = await self.voice_gateway.poll_event()
            # Событие уже обработано в _handle_message, просто ждем следующее
        
        # Обновить данные из voice_gateway
        self.ssrc = self.voice_gateway.ssrc
        self.udp_ip = self.voice_gateway.ip
        self.udp_port = self.voice_gateway.port
        
        # Настроить UDP и отправить SELECT_PROTOCOL
        await self._setup_udp()
        
        # Ждать SESSION_DESCRIPTION (получение secret_key)
        while not self.voice_gateway.secret_key:
            event = await self.voice_gateway.poll_event()
            # Событие уже обработано в _handle_message, просто ждем следующее
        
        self.secret_key = self.voice_gateway.secret_key
        self.ready = True
    
    def _on_voice_ready(self, data: Dict):
        """Обработчик готовности Voice Gateway (для совместимости, но не используется в синхронном handshake)"""
        # Данные уже установлены в _handshake_voice_gateway
    
    def _on_session_description(self, data: Dict):
        """Обработчик session description"""
        self.secret_key = bytes(data.get("secret_key", []))
        self.ready = True
    
    async def _setup_udp(self):
        """Настроить UDP соединение"""
        # Защита от двойного вызова
        if self._udp_setup_in_progress:
            logger.warning("⚠️ UDP setup already in progress, skipping...")
            return
        
        self._udp_setup_in_progress = True
        try:
            if not self.ssrc or not self.udp_ip or not self.udp_port:
                logger.error(f"❌ Missing UDP info: ssrc={self.ssrc}, udp_ip={self.udp_ip}, udp_port={self.udp_port}")
                return
            
            # Создать UDP socket
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setblocking(False)
            
            # Подключиться к UDP сокету (как в discord.py)
            loop = asyncio.get_event_loop()
            await loop.sock_connect(self.udp_socket, (self.udp_ip, self.udp_port))
            
            # Отправить discovery packet (74 bytes как в discord.py)
            packet = bytearray(74)
            struct.pack_into('>H', packet, 0, 1)  # Type = 1 (Send)
            struct.pack_into('>H', packet, 2, 70)  # Length = 70
            struct.pack_into('>I', packet, 4, self.ssrc)  # SSRC
            
            await loop.sock_sendall(self.udp_socket, bytes(packet))
            
            # Получить ответ (как в discord.py - ожидаем 74 bytes, тип 0x02)
            try:
                data = await asyncio.wait_for(
                    loop.sock_recv(self.udp_socket, 74),
                    timeout=5.0
                )
                
                if len(data) == 74 and data[1] == 0x02:
                    # IP начинается с 8-го байта и заканчивается первым null
                    ip_start = 8
                    ip_end = data.index(0, ip_start)
                    self.local_ip = data[ip_start:ip_end].decode('ascii')
                    # Порт в последних 2 байтах
                    self.local_port = struct.unpack_from('>H', data, len(data) - 2)[0]
                else:
                    raise ValueError(f"Invalid UDP response: length={len(data)}, type={data[1] if len(data) > 1 else 'N/A'}")
            except asyncio.TimeoutError:
                logger.warning("⚠️ UDP discovery timeout, using default values")
                self.local_ip = "127.0.0.1"
                self.local_port = 0
            except Exception as e:
                logger.warning(f"⚠️ UDP discovery failed: {e}, using default", exc_info=True)
                self.local_ip = "127.0.0.1"
                self.local_port = 0
            
            # Выбрать режим шифрования из поддерживаемых (как в discord.py)
            if self.voice_gateway and self.voice_gateway.modes:
                # Поддерживаемые режимы (как в discord.py)
                supported_modes = [
                    'aead_xchacha20_poly1305_rtpsize',
                    'xsalsa20_poly1305_lite',
                    'xsalsa20_poly1305_suffix',
                    'xsalsa20_poly1305'
                ]
                modes = [mode for mode in self.voice_gateway.modes if mode in supported_modes]
                if not modes:
                    logger.warning("⚠️ No supported encryption modes found, using first available")
                    mode = self.voice_gateway.modes[0]
                else:
                    mode = modes[0]
            else:
                mode = "xsalsa20_poly1305_lite"
                logger.warning(f"⚠️ Using default encryption mode: {mode}")
            
            # Сохранить режим шифрования
            self.encryption_mode = mode
            
            # Отправить SELECT_PROTOCOL с реальным IP и портом (или дефолтными значениями)
            if self.voice_gateway:
                try:
                    await self.voice_gateway._select_protocol(self.local_ip, self.local_port, mode)
                except Exception as e:
                    logger.error(f"❌ Failed to send SELECT_PROTOCOL: {e}", exc_info=True)
                    raise
            else:
                logger.error("❌ Voice Gateway is None, cannot send SELECT_PROTOCOL")
                raise RuntimeError("Voice Gateway is None")
        
        except Exception as e:
            logger.error(f"❌ Failed to setup UDP: {e}", exc_info=True)
            raise
        finally:
            self._udp_setup_in_progress = False
    
    async def disconnect(self, *, force: bool = False) -> None:
        """Отключиться от голосового канала"""
        # Остановить воспроизведение
        try:
            await self.stop()
        except Exception as e:
            logger.warning(f"Error stopping playback: {e}")
        
        # Отключиться от Voice Gateway
        if self.voice_gateway:
            try:
                await self.voice_gateway.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting voice gateway: {e}")
            self.voice_gateway = None
        
        # Закрыть UDP socket
        if self.udp_socket:
            self.udp_socket.close()
            self.udp_socket = None
        
        # Обновить voice state
        if self.guild:
            await self._update_voice_state(None, False, False)
            # Удалить из voice_clients
            if self.guild.id in self.client.voice_clients:
                del self.client.voice_clients[self.guild.id]
        
        self.connected = False
        self.ready = False
        logger.info(f"Disconnected from voice channel {self.channel.id}")
    
    async def move_to(self, channel: 'Channel') -> None:
        """Переместиться в другой голосовой канал"""
        if not self.connected:
            raise RuntimeError("Cannot move: not connected")
        
        await self._update_voice_state(channel.id, False, False)
        self.channel = channel
        logger.info(f"Moved to voice channel {channel.id}")
    
    def is_connected(self) -> bool:
        """Проверить, подключен ли клиент"""
        return self.connected
    
    def is_playing(self) -> bool:
        """Проверить, воспроизводится ли аудио"""
        return self.playing
    
    def is_paused(self) -> bool:
        """Проверить, поставлено ли на паузу"""
        return self.paused
    
    async def play(self, source: 'AudioSource', *, after: Optional[Callable] = None):
        """Воспроизвести аудио источник"""
        # Дождаться готовности
        if not self.ready:
            timeout = 10.0  # 10 секунд таймаут
            start_time = time.time()
            while not self.ready and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.1)
            
            if not self.ready:
                raise RuntimeError("Voice client not ready after timeout")
        
        if self.playing:
            await self.stop()
        
        self.audio_source = source
        self.playing = True
        self.paused = False
        
        # Установить speaking (важно: нужно отправить перед началом отправки аудио)
        if self.voice_gateway:
            await self.voice_gateway.set_speaking(True)
            # Небольшая задержка, чтобы Discord успел обработать SPEAKING
            await asyncio.sleep(0.1)
        
        # Запустить задачу воспроизведения
        self.audio_task = asyncio.create_task(self._audio_loop(after))
    
    async def _audio_loop(self, after: Optional[Callable] = None):
        """Цикл воспроизведения аудио"""
        import time
        
        try:
            # Инициализировать Opus encoder если нужно
            if not self.audio_source.is_opus():
                if OPUS_AVAILABLE:
                    try:
                        import opuslib
                        self.encoder = opuslib.Encoder(48000, 2, opuslib.APPLICATION_AUDIO)
                    except Exception as e:
                        logger.error(f"❌ Failed to initialize Opus encoder: {e}", exc_info=True)
                        self.encoder = None
                else:
                    logger.error("❌ Opus not available, cannot encode PCM audio! Install opuslib.")
                    self.encoder = None
            
            # Предварительная буферизация: читаем несколько пакетов перед началом
            buffer_size = 3  # Буферизуем 3 пакета (60ms)
            buffer = []
            for _ in range(buffer_size):
                data = self.audio_source.read()
                if not data:
                    break
                    buffer.append(data)
            
            packet_count = 0
            frame_duration = 0.02  # 20ms для Opus кадров
            start_time = time.perf_counter()
            
            while self.playing and self.audio_source:
                if self.paused:
                    await asyncio.sleep(0.1)
                    start_time = time.perf_counter() - (packet_count * frame_duration)  # Сбросить время при паузе
                    continue
                
                # Использовать буферизованные пакеты, если есть
                if buffer:
                    data = buffer.pop(0)
                else:
                    # Прочитать данные
                    data = self.audio_source.read()
                    if not data:
                        # Проверяем, может быть источник еще не закончился
                        # Даем небольшую задержку перед окончательным решением
                        await asyncio.sleep(0.01)
                        data = self.audio_source.read()
                        if not data:
                            break
                
                # Кодировать в Opus если нужно
                if not self.audio_source.is_opus():
                    if not self.encoder:
                        logger.error("❌ Cannot encode PCM audio: Opus encoder not available!")
                        break
                    try:
                        data = self.encoder.encode(data, 960)  # 20ms frame
                    except Exception as e:
                        logger.error(f"❌ Opus encoding error: {e}", exc_info=True)
                        break
                
                # Отправить через UDP
                try:
                    await self._send_audio_packet(data)
                    packet_count += 1
                except Exception as e:
                    logger.error(f"❌ Error sending audio packet #{packet_count}: {e}", exc_info=True)
                    break
                
                # Точная синхронизация времени для 20ms кадров
                next_time = start_time + (packet_count * frame_duration)
                current_time = time.perf_counter()
                delay = next_time - current_time
                
                if delay > 0:
                    await asyncio.sleep(delay)
                elif delay < -0.1:  # Если отстаем больше чем на 100ms, сбросить время
                    start_time = time.perf_counter() - (packet_count * frame_duration)
        
        except Exception as e:
            logger.error(f"Error in audio loop: {e}", exc_info=True)
        finally:
            self.playing = False
            if self.voice_gateway:
                try:
                    await self.voice_gateway.set_speaking(False)
                except Exception as e:
                    logger.warning(f"Failed to set speaking to False: {e}")
            
            # Вызвать after callback если он есть и является callable
            if after is not None:
                try:
                    if callable(after):
                        if asyncio.iscoroutinefunction(after):
                            await after(None)
                        else:
                            after(None)
                    else:
                        logger.warning(f"after callback is not callable: {type(after)}")
                except Exception as e:
                    logger.error(f"Error in after callback: {e}", exc_info=True)
    
    async def _send_audio_packet(self, data: bytes):
        """Отправить аудио пакет через UDP (как в discord.py)"""
        if not self.udp_socket or not self.secret_key or not self.udp_ip or not self.udp_port:
            logger.warning(f"⚠️ Cannot send audio packet: missing required data (socket={bool(self.udp_socket)}, key={bool(self.secret_key)}, ip={self.udp_ip}, port={self.udp_port})")
            return
        
        if not self.encryption_mode:
            logger.error("❌ Encryption mode not set, cannot encrypt audio")
            return
        
        if not data:
            logger.warning("⚠️ Empty audio data, skipping packet")
            return
        
        # Создать RTP заголовок
        header = bytearray(12)
        header[0] = 0x80  # Version, padding, extension, CC
        header[1] = 0x78  # Marker, payload type (Opus = 120)
        struct.pack_into('>H', header, 2, self.sequence)
        struct.pack_into('>I', header, 4, self.timestamp)
        struct.pack_into('>I', header, 8, self.ssrc)
        
        # Зашифровать данные в зависимости от режима (как в discord.py)
        if not NACL_AVAILABLE:
            logger.error("PyNaCl not available, cannot encrypt audio")
            return
        
        try:
            from nacl.secret import SecretBox
            
            if self.encryption_mode == 'aead_xchacha20_poly1305_rtpsize':
                # Используем AEAD с инкрементирующимся nonce (как в discord.py)
                try:
                    from nacl.secret import Aead
                    box = Aead(self.secret_key)
                    nonce = bytearray(24)
                    nonce[:4] = struct.pack('>I', self._incr_nonce)
                    encrypted = box.encrypt(bytes(data), bytes(header), bytes(nonce)).ciphertext
                    packet = header + encrypted + nonce[:4]  # Добавляем nonce в конец
                    self._incr_nonce = (self._incr_nonce + 1) % 4294967296
                except ImportError:
                    logger.error("❌ Aead not available, cannot use aead_xchacha20_poly1305_rtpsize mode")
                    return
                except Exception as e:
                    logger.error(f"❌ Failed to encrypt with Aead: {e}", exc_info=True)
                    return
                
            elif self.encryption_mode == 'xsalsa20_poly1305_lite':
                # Используем SecretBox с инкрементирующимся nonce
                box = SecretBox(self.secret_key)
                nonce = bytearray(24)
                nonce[:4] = struct.pack('>I', self._incr_nonce)
                encrypted = box.encrypt(bytes(data), bytes(nonce)).ciphertext
                packet = header + encrypted + nonce[:4]  # Добавляем nonce в конец
                self._incr_nonce = (self._incr_nonce + 1) % 4294967296
                
            elif self.encryption_mode == 'xsalsa20_poly1305_suffix':
                # Используем SecretBox со случайным nonce
                import nacl.utils
                box = SecretBox(self.secret_key)
                nonce = nacl.utils.random(24)
                encrypted = box.encrypt(bytes(data), nonce).ciphertext
                packet = header + encrypted + nonce
                
            elif self.encryption_mode == 'xsalsa20_poly1305':
                # Используем SecretBox с nonce из заголовка
                box = SecretBox(self.secret_key)
                nonce = bytearray(24)
                nonce[:12] = header
                encrypted = box.encrypt(bytes(data), bytes(nonce)).ciphertext
                packet = header + encrypted
                
            else:
                logger.error(f"❌ Unknown encryption mode: {self.encryption_mode}")
                return
            
            # Отправить через подключенный UDP сокет (как в discord.py)
            loop = asyncio.get_event_loop()
            await loop.sock_sendall(self.udp_socket, packet)
            
            # Обновить счетчики
            self.sequence = (self.sequence + 1) % 65536
            self.timestamp = (self.timestamp + 960) % 4294967296  # 20ms = 960 samples
        
        except Exception as e:
            logger.error(f"❌ Failed to send audio packet: {e}", exc_info=True)
            raise  # Пробросить исключение, чтобы увидеть проблему
    
    async def stop(self):
        """Остановить воспроизведение"""
        self.playing = False
        self.paused = False
        
        if self.audio_task:
            self.audio_task.cancel()
            try:
                await self.audio_task
            except asyncio.CancelledError:
                pass
            self.audio_task = None
        
        if self.audio_source:
            if hasattr(self.audio_source, 'cleanup'):
                self.audio_source.cleanup()
            self.audio_source = None
        
        if self.voice_gateway and self.voice_gateway.running:
            try:
                await self.voice_gateway.set_speaking(False)
            except Exception as e:
                logger.warning(f"Failed to set speaking to False: {e}")
    
    async def pause(self):
        """Поставить на паузу"""
        if not self.playing:
            return
        self.paused = True
        if self.voice_gateway:
            await self.voice_gateway.set_speaking(False)
    
    async def resume(self):
        """Возобновить воспроизведение"""
        if not self.playing or not self.paused:
            return
        self.paused = False
        if self.voice_gateway:
            await self.voice_gateway.set_speaking(True)
    
    def set_volume(self, volume: float):
        """Установить громкость (0.0 - 2.0)"""
        self.volume = max(0.0, min(2.0, volume))
    
    def get_volume(self) -> float:
        """Получить текущую громкость"""
        return self.volume
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


# Утилиты для работы с Voice
async def connect_to_voice(client: 'Client', channel: 'Channel', **kwargs) -> VoiceClient:
    """Подключиться к голосовому каналу"""
    voice_client = VoiceClient(client, channel)
    await voice_client.connect(**kwargs)
    return voice_client

