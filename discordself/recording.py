"""Recording support для Voice"""

import asyncio
import logging
import struct
from typing import Optional, Callable, BinaryIO
from .voice import VoiceClient

logger = logging.getLogger(__name__)

# Использовать тот же код загрузки opus.dll, что и в voice.py
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
        import ctypes
        dll_dir = os.path.dirname(opus_dll_path)
        if sys.platform == 'win32':
            current_path = os.environ.get('PATH', '')
            os.environ['PATH'] = dll_dir + os.pathsep + current_path
        ctypes.CDLL(opus_dll_path)
    except Exception:
        pass

try:
    import opuslib
    if opus_dll_path and hasattr(opuslib, 'load_opus'):
        try:
            opuslib.load_opus(opus_dll_path)
        except Exception:
            pass
    # Проверить работоспособность
    test_decoder = opuslib.Decoder(48000, 2)
    del test_decoder
    OPUS_AVAILABLE = True
except (ImportError, Exception) as e:
    OPUS_AVAILABLE = False
    logger.warning(f"opuslib not available. Recording will not work. Error: {e}. Install with: pip install opuslib")


class AudioSink:
    """Базовый класс для записи аудио"""
    
    def write(self, user_id: int, data: bytes):
        """Записать аудио данные"""
        raise NotImplementedError("Sink must implement write() method")
    
    def cleanup(self):
        """Очистить ресурсы"""
        pass


class FileSink(AudioSink):
    """Запись аудио в файл"""
    
    def __init__(self, filename: str, user_id: Optional[int] = None):
        self.filename = filename
        self.user_id = user_id
        self.file: Optional[BinaryIO] = None
        self.decoder = None
        
        # Открыть файл
        self.file = open(filename, 'wb')
    
    def write(self, user_id: int, data: bytes):
        """Записать аудио данные в файл"""
        if self.user_id is not None and user_id != self.user_id:
            return
        
        if self.file:
            # Записать размер пакета и данные
            self.file.write(struct.pack('>H', len(data)))
            self.file.write(data)
    
    def cleanup(self):
        """Закрыть файл"""
        if self.file:
            self.file.close()
            self.file = None


class PCMFileSink(AudioSink):
    """Запись PCM аудио в файл"""
    
    def __init__(self, filename: str, user_id: Optional[int] = None, 
                 sample_rate: int = 48000, channels: int = 2):
        self.filename = filename
        self.user_id = user_id
        self.sample_rate = sample_rate
        self.channels = channels
        self.file: Optional[BinaryIO] = None
        self.decoder = None
        
        if OPUS_AVAILABLE:
            try:
                import opuslib
                self.decoder = opuslib.Decoder(sample_rate, channels)
            except Exception as e:
                logger.error(f"Failed to initialize Opus decoder: {e}")
                self.decoder = None
        
        # Открыть файл
        self.file = open(filename, 'wb')
    
    def write(self, user_id: int, data: bytes):
        """Записать PCM данные в файл"""
        if self.user_id is not None and user_id != self.user_id:
            return
        
        if not self.file:
            return
        
        # Декодировать Opus в PCM если нужно
        if self.decoder:
            try:
                pcm_data = self.decoder.decode(data, 960)  # 20ms frame
                self.file.write(pcm_data)
            except Exception as e:
                logger.error(f"Failed to decode Opus data: {e}")
        else:
            # Записать как есть
            self.file.write(data)
    
    def cleanup(self):
        """Закрыть файл"""
        if self.file:
            self.file.close()
            self.file = None


class RecordingVoiceClient(VoiceClient):
    """VoiceClient с поддержкой записи"""
    
    def __init__(self, client, channel):
        super().__init__(client, channel)
        self.sinks: list[AudioSink] = []
        self.recording = False
        self._recording_task: Optional[asyncio.Task] = None
    
    def add_sink(self, sink: AudioSink):
        """Добавить sink для записи"""
        self.sinks.append(sink)
    
    def remove_sink(self, sink: AudioSink):
        """Удалить sink"""
        if sink in self.sinks:
            self.sinks.remove(sink)
            sink.cleanup()
    
    async def start_recording(self):
        """Начать запись"""
        if self.recording:
            return
        
        if not self.ready:
            raise RuntimeError("Voice client not ready")
        
        self.recording = True
        self._recording_task = asyncio.create_task(self._recording_loop())
        logger.info("Started recording")
    
    async def stop_recording(self):
        """Остановить запись"""
        if not self.recording:
            return
        
        self.recording = False
        
        if self._recording_task:
            self._recording_task.cancel()
            try:
                await self._recording_task
            except asyncio.CancelledError:
                pass
            self._recording_task = None
        
        # Очистить sinks
        for sink in self.sinks:
            sink.cleanup()
        
        logger.info("Stopped recording")
    
    async def _recording_loop(self):
        """Цикл записи аудио"""
        # В реальной реализации здесь будет получение аудио пакетов от Discord
        # и их запись в sinks
        # Это требует дополнительной реализации UDP receiving
        pass
    
    async def disconnect(self, *, force: bool = False):
        """Отключиться и остановить запись"""
        await self.stop_recording()
        await super().disconnect(force=force)

