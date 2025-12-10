"""Voice Gateway клиент для Discord"""

import asyncio
import json
import logging
import struct
import time
from typing import Optional, Dict, Any, Callable
import websockets
from .exceptions import WebSocketException

logger = logging.getLogger(__name__)


class VoiceOpcode:
    """Opcode для Voice Gateway"""
    IDENTIFY = 0
    SELECT_PROTOCOL = 1
    READY = 2
    HEARTBEAT = 3
    SESSION_DESCRIPTION = 4
    SPEAKING = 5
    HEARTBEAT_ACK = 6
    RESUME = 7
    HELLO = 8
    RESUMED = 9
    CLIENT_DISCONNECT = 13


class VoiceGatewayClient:
    """WebSocket клиент для Voice Gateway"""
    
    def __init__(self, endpoint: str, token: str, session_id: str, guild_id: int, user_id: int):
        self.endpoint = endpoint
        self.token = token
        self.session_id = session_id
        self.guild_id = guild_id
        self.user_id = user_id
        
        self.ws = None  # websockets.WebSocketClientProtocol
        self.running = False
        self.heartbeat_interval: Optional[float] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.listen_task: Optional[asyncio.Task] = None
        self.sequence: int = 0
        
        # Callbacks
        self.on_ready: Optional[Callable] = None
        self.on_session_description: Optional[Callable] = None
        self.on_speaking: Optional[Callable] = None
        
        # Voice server info
        self.ssrc: Optional[int] = None
        self.port: Optional[int] = None
        self.ip: Optional[str] = None
        self.modes: list = []
        self.secret_key: Optional[bytes] = None
        
        # Event queue for poll_event
        self._event_queue: asyncio.Queue = asyncio.Queue()
    async def connect(self):
        """Подключиться к Voice Gateway"""
        # Убрать wss:// префикс если есть
        endpoint = self.endpoint
        if endpoint.startswith('wss://'):
            endpoint = endpoint[6:]
        # Убрать порт из endpoint если есть
        endpoint = endpoint.split(':')[0] if ':' in endpoint else endpoint
        url = f"wss://{endpoint}?v=4"
        
        logger.info(f"🔌 Connecting to Voice Gateway: {url} (endpoint={self.endpoint})")
        
        try:
            self.ws = await websockets.connect(url)
            self.running = True
            
            # Запустить listener
            self.listen_task = asyncio.create_task(self._listen())
            
            # Отправить IDENTIFY
            await self._identify()
            
        except Exception as e:
            logger.error(f"Failed to connect to Voice Gateway: {e}")
            raise WebSocketException(0, str(e))
    
    def _get_close_code_description(self, code: int) -> str:
        """Получить описание кода закрытия"""
        codes = {
            4001: "Unknown opcode",
            4002: "Failed to decode payload",
            4003: "Not authenticated",
            4004: "Authentication failed",
            4005: "Already authenticated",
            4006: "Session no longer valid",
            4009: "Session timeout",
            4011: "Server not found",
            4012: "Unknown protocol",
            4014: "Disconnected",
            4015: "Voice server crashed",
            4016: "Unknown encryption mode",
            4020: "Bad Request - Invalid payload or protocol"
        }
        return codes.get(code, "Unknown error")
    
    async def disconnect(self):
        """Отключиться от Voice Gateway"""
        self.running = False
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            self.heartbeat_task = None
        
        if self.listen_task:
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass
            self.listen_task = None
        
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                logger.warning(f"Error closing Voice Gateway WebSocket: {e}")
            self.ws = None
    
    async def _listen(self):
        """Слушать сообщения от Voice Gateway"""
        while self.running and self.ws:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                # Добавить в очередь для poll_event
                await self._event_queue.put(data)
                # Также обработать через callback
                await self._handle_message(data)
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"Voice Gateway connection closed: code={e.code}, reason={e.reason}")
                if e.code:
                    logger.warning(f"Close code details: {e.code} - {self._get_close_code_description(e.code)}")
                break
            except Exception as e:
                logger.error(f"Error in Voice Gateway listener: {e}")
                await asyncio.sleep(1)
    
    async def poll_event(self):
        """Получить следующее событие из очереди (для синхронного handshake)"""
        return await self._event_queue.get()
    
    async def _handle_message(self, data: Dict):
        """Обработать сообщение от Voice Gateway"""
        op = data.get("op")
        event_data = data.get("d")
        
        if op == VoiceOpcode.HELLO:
            self.heartbeat_interval = event_data.get("heartbeat_interval") / 1000.0
            logger.info(f"Voice Gateway HELLO, heartbeat interval: {self.heartbeat_interval}s")
            
            # Запустить heartbeat
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        elif op == VoiceOpcode.READY:
            self.ssrc = event_data.get("ssrc")
            self.port = event_data.get("port")
            self.ip = event_data.get("ip")
            self.modes = event_data.get("modes", [])
            logger.info(f"🎉 Voice Gateway READY event: ssrc={self.ssrc}, ip={self.ip}, port={self.port}, modes={self.modes}")
            
            # Выбрать протокол (будет вызван после UDP discovery)
            # await self._select_protocol()
            
            if self.on_ready:
                logger.info("📞 Calling on_ready callback...")
                try:
                    self.on_ready(event_data)
                except Exception as e:
                    logger.error(f"❌ Error in on_ready callback: {e}", exc_info=True)
            else:
                logger.warning("⚠️ No on_ready callback set!")
        
        elif op == VoiceOpcode.SESSION_DESCRIPTION:
            self.secret_key = bytes(event_data.get("secret_key", []))
            logger.info(f"🎉 Voice Gateway SESSION_DESCRIPTION event received, secret_key length={len(self.secret_key)}")
            
            if self.on_session_description:
                logger.info("📞 Calling on_session_description callback...")
                try:
                    self.on_session_description(event_data)
                except Exception as e:
                    logger.error(f"❌ Error in on_session_description callback: {e}", exc_info=True)
            else:
                logger.warning("⚠️ No on_session_description callback set!")
        
        elif op == VoiceOpcode.SPEAKING:
            if self.on_speaking:
                self.on_speaking(event_data)
        
        elif op == VoiceOpcode.HEARTBEAT_ACK:
            logger.debug("Voice Gateway HEARTBEAT_ACK")
    
    async def _identify(self):
        """Отправить IDENTIFY"""
        payload = {
            "op": VoiceOpcode.IDENTIFY,
            "d": {
                "server_id": str(self.guild_id),
                "user_id": str(self.user_id),
                "session_id": self.session_id,
                "token": self.token
            }
        }
        await self._send(payload)
        logger.info("Sent Voice Gateway IDENTIFY")
    
    async def _select_protocol(self, local_ip: Optional[str] = None, local_port: Optional[int] = None, mode: Optional[str] = None):
        """Выбрать протокол (как в discord.py)"""
        # Если режим не указан, выбрать из поддерживаемых
        if not mode:
            # Поддерживаемые режимы (как в discord.py)
            supported_modes = [
                'aead_xchacha20_poly1305_rtpsize',
                'xsalsa20_poly1305_lite',
                'xsalsa20_poly1305_suffix',
                'xsalsa20_poly1305'
            ]
            modes = [m for m in self.modes if m in supported_modes]
            if modes:
                mode = modes[0]
            else:
                mode = self.modes[0] if self.modes else "xsalsa20_poly1305"
        
        logger.info(f"📤 Preparing SELECT_PROTOCOL: mode={mode}, local_ip={local_ip}, local_port={local_port}, available_modes={self.modes}")
        
        payload = {
            "op": VoiceOpcode.SELECT_PROTOCOL,
            "d": {
                "protocol": "udp",
                "data": {
                    "address": local_ip or "127.0.0.1",
                    "port": local_port or 0,
                    "mode": mode
                }
            }
        }
        logger.info(f"📤 Sending SELECT_PROTOCOL payload: {payload}")
        await self._send(payload)
        logger.info(f"✅ Sent Voice Gateway SELECT_PROTOCOL: {mode} (ip={local_ip}, port={local_port})")
    
    async def _heartbeat_loop(self):
        """Цикл отправки heartbeat"""
        while self.running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                if self.running:
                    await self._heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in Voice Gateway heartbeat loop: {e}")
    
    async def _heartbeat(self):
        """Отправить heartbeat"""
        payload = {
            "op": VoiceOpcode.HEARTBEAT,
            "d": int(time.time() * 1000)
        }
        await self._send(payload)
        logger.debug("Sent Voice Gateway HEARTBEAT")
    
    async def set_speaking(self, speaking: bool = True, delay: int = 0):
        """Установить статус speaking"""
        payload = {
            "op": VoiceOpcode.SPEAKING,
            "d": {
                "speaking": 1 if speaking else 0,
                "delay": delay,
                "ssrc": self.ssrc
            }
        }
        await self._send(payload)
    
    async def _send(self, payload: Dict):
        """Отправить сообщение в Voice Gateway"""
        if self.ws and self.running:
            try:
                await self.ws.send(json.dumps(payload))
            except Exception as e:
                # Если соединение закрыто, не поднимать исключение
                if "ConnectionClosed" in str(type(e).__name__) or "4006" in str(e):
                    logger.warning(f"Voice Gateway connection closed, ignoring send: {e}")
                    self.running = False
                    return
                logger.error(f"Failed to send message to Voice Gateway: {e}")
                raise WebSocketException(0, str(e))
        else:
            logger.warning("Cannot send message: Voice Gateway not connected")

