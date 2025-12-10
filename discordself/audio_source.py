"""Источники аудио для Voice"""

import asyncio
import io
import struct
from typing import Optional, Any, Callable
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class AudioSource(ABC):
    """Базовый класс для источников аудио"""
    
    def __init__(self):
        self.cleanup: Optional[Callable] = None
    
    @abstractmethod
    def read(self) -> bytes:
        """Прочитать порцию аудио данных"""
        raise NotImplementedError
    
    @abstractmethod
    def is_opus(self) -> bool:
        """Проверить, является ли аудио Opus"""
        raise NotImplementedError
    
    def cleanup(self):
        """Очистить ресурсы"""
        if self.cleanup:
            self.cleanup()


class PCMAudioSource(AudioSource):
    """Источник PCM аудио (требует кодирования в Opus)"""
    
    def __init__(self, stream: Any, sample_rate: int = 48000, channels: int = 2):
        super().__init__()
        self.stream = stream
        self.sample_rate = sample_rate
        self.channels = channels
        self.frame_size = 20  # 20ms frames
    
    def read(self) -> bytes:
        """Прочитать PCM данные"""
        # 20ms = 48000 * 0.02 = 960 samples per channel
        # 2 channels = 1920 samples
        # 16-bit = 2 bytes per sample
        # Total = 1920 * 2 = 3840 bytes
        frame_size = int(self.sample_rate * self.frame_size / 1000) * self.channels * 2
        data = self.stream.read(frame_size)
        return data
    
    def is_opus(self) -> bool:
        return False


class OpusAudioSource(AudioSource):
    """Источник Opus аудио (уже закодирован)"""
    
    def __init__(self, stream: Any):
        super().__init__()
        self.stream = stream
    
    def read(self) -> bytes:
        """Прочитать Opus данные"""
        # Читать длину пакета (2 bytes)
        length_bytes = self.stream.read(2)
        if len(length_bytes) < 2:
            return b''
        
        length = struct.unpack('>H', length_bytes)[0]
        if length == 0:
            return b''
        
        # Читать данные пакета
        data = self.stream.read(length)
        return data
    
    def is_opus(self) -> bool:
        return True


class FileAudioSource(OpusAudioSource):
    """Источник аудио из файла"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.file = open(filename, 'rb')
        super().__init__(self.file)
    
    def cleanup(self):
        """Закрыть файл"""
        if self.file:
            self.file.close()


class BytesAudioSource(AudioSource):
    """Источник аудио из байтов"""
    
    def __init__(self, data: bytes, is_opus: bool = False):
        super().__init__()
        self.data = data
        self._is_opus = is_opus
        self.position = 0
    
    def read(self) -> bytes:
        """Прочитать данные"""
        if self.position >= len(self.data):
            return b''
        
        # Читать порцию данных (20ms для PCM, или пакет для Opus)
        chunk_size = 3840 if not self._is_opus else 4000
        chunk = self.data[self.position:self.position + chunk_size]
        self.position += chunk_size
        return chunk
    
    def is_opus(self) -> bool:
        return self._is_opus


class SilenceSource(AudioSource):
    """Источник тишины (для тестирования)"""
    
    def __init__(self, duration: float = 1.0, sample_rate: int = 48000, channels: int = 2):
        super().__init__()
        self.duration = duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.frame_size = 20  # 20ms
        self.frames_sent = 0
        self.total_frames = int((duration * 1000) / self.frame_size)
    
    def read(self) -> bytes:
        """Прочитать тишину"""
        if self.frames_sent >= self.total_frames:
            return b''
        
        # 20ms тишины
        frame_size = int(self.sample_rate * self.frame_size / 1000) * self.channels * 2
        self.frames_sent += 1
        return b'\x00' * frame_size
    
    def is_opus(self) -> bool:
        return False


class VolumeTransformer(AudioSource):
    """Трансформер громкости для аудио источника"""
    
    def __init__(self, original: AudioSource, volume: float = 1.0):
        super().__init__()
        self.original = original
        self.volume = max(0.0, min(2.0, volume))  # Ограничить от 0.0 до 2.0
    
    def read(self) -> bytes:
        """Прочитать данные с применением громкости"""
        data = self.original.read()
        
        if not data or self.volume == 1.0:
            return data
        
        # Применить громкость к PCM данным
        if not self.original.is_opus():
            import struct
            # Конвертировать в список samples
            samples = list(struct.unpack(f'<{len(data)//2}h', data))
            # Применить громкость
            samples = [int(sample * self.volume) for sample in samples]
            # Ограничить значения
            samples = [max(-32768, min(32767, sample)) for sample in samples]
            # Конвертировать обратно в bytes
            data = struct.pack(f'<{len(samples)}h', *samples)
        
        return data
    
    def is_opus(self) -> bool:
        return self.original.is_opus()
    
    def cleanup(self):
        """Очистить ресурсы"""
        if hasattr(self.original, 'cleanup'):
            self.original.cleanup()


class AudioFilter:
    """Базовый класс для аудио фильтров"""
    
    def apply(self, data: bytes, sample_rate: int = 48000, channels: int = 2) -> bytes:
        """Применить фильтр к аудио данным"""
        raise NotImplementedError("Filter must implement apply() method")


class LowPassFilter(AudioFilter):
    """Низкочастотный фильтр"""
    
    def __init__(self, cutoff: float = 3000.0):
        self.cutoff = cutoff
        self._prev_samples = None
    
    def apply(self, data: bytes, sample_rate: int = 48000, channels: int = 2) -> bytes:
        """Применить низкочастотный фильтр"""
        import struct
        import math
        
        # Упрощенная реализация RC фильтра
        rc = 1.0 / (2.0 * math.pi * self.cutoff)
        dt = 1.0 / sample_rate
        alpha = dt / (rc + dt)
        
        samples = list(struct.unpack(f'<{len(data)//2}h', data))
        
        if self._prev_samples is None:
            self._prev_samples = [0.0] * channels
        
        filtered = []
        for i, sample in enumerate(samples):
            channel = i % channels
            prev = self._prev_samples[channel]
            filtered_sample = prev + alpha * (sample - prev)
            self._prev_samples[channel] = filtered_sample
            filtered.append(int(filtered_sample))
        
        return struct.pack(f'<{len(filtered)}h', *filtered)


class FilteredAudioSource(AudioSource):
    """Аудио источник с применением фильтров"""
    
    def __init__(self, original: AudioSource, *filters: AudioFilter):
        super().__init__()
        self.original = original
        self.filters = list(filters)
        self.sample_rate = 48000
        self.channels = 2
    
    def read(self) -> bytes:
        """Прочитать данные с применением фильтров"""
        data = self.original.read()
        
        if not data or not self.filters or self.original.is_opus():
            return data
        
        # Применить фильтры
        for filter in self.filters:
            data = filter.apply(data, self.sample_rate, self.channels)
        
        return data
    
    def is_opus(self) -> bool:
        return self.original.is_opus()
    
    def cleanup(self):
        """Очистить ресурсы"""
        if hasattr(self.original, 'cleanup'):
            self.original.cleanup()

