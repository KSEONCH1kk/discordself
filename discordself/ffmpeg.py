"""FFmpeg integration для аудио источников"""

import asyncio
import subprocess
import logging
from typing import Optional, Any, Iterator
from .audio_source import AudioSource, PCMAudioSource
from .oggparse import OggStream

logger = logging.getLogger(__name__)


class FFmpegPCMAudio(PCMAudioSource):
    """Аудио источник из FFmpeg процесса"""
    
    def __init__(self, source: str, *, executable: str = 'ffmpeg', 
                 before_options: Optional[str] = None, options: Optional[str] = None,
                 sample_rate: int = 48000, channels: int = 2):
        self.source = source
        self.executable = executable
        self.before_options = before_options or ''
        self.options = options or '-f s16le -ar {sample_rate} -ac {channels}'
        self.sample_rate = sample_rate
        self.channels = channels
        
        # Форматировать options
        self.options = self.options.format(sample_rate=sample_rate, channels=channels)
        
        # Создать процесс
        self.process: Optional[subprocess.Popen] = None
        self._stdout: Optional[Any] = None
        
        super().__init__(None, sample_rate, channels)
    
    def _spawn_process(self):
        """Запустить FFmpeg процесс"""
        command = [
            self.executable,
            '-i', self.source,
        ]
        
        if self.before_options:
            command.extend(self.before_options.split())
        
        command.extend([
            '-f', 's16le',
            '-ar', str(self.sample_rate),
            '-ac', str(self.channels),
            '-loglevel', 'warning',
            '-'
        ])
        
        if self.options:
            command.extend(self.options.split())
        
        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self._stdout = self.process.stdout
            self.stream = self._stdout
            logger.info(f"Started FFmpeg process for {self.source}")
        except FileNotFoundError:
            raise RuntimeError(f"FFmpeg executable '{self.executable}' not found. Please install FFmpeg.")
        except Exception as e:
            raise RuntimeError(f"Failed to start FFmpeg process: {e}")
    
    def read(self) -> bytes:
        """Прочитать PCM данные"""
        if self.process is None:
            self._spawn_process()
        
        if self.process.poll() is not None:
            # Процесс завершился
            stderr = self.process.stderr.read().decode('utf-8', errors='ignore') if self.process.stderr else ""
            if stderr:
                logger.warning(f"FFmpeg process ended. stderr: {stderr[:200]}")
            return b''
        
        # Читать 20ms данных (960 samples * 2 channels * 2 bytes per sample = 3840 bytes)
        frame_size = int(self.sample_rate * 0.02) * self.channels * 2
        data = self._stdout.read(frame_size)
        
        if not data:
            # Проверить, не завершился ли процесс
            if self.process.poll() is not None:
                stderr = self.process.stderr.read().decode('utf-8', errors='ignore') if self.process.stderr else ""
                if stderr:
                    logger.warning(f"FFmpeg process ended. stderr: {stderr[:200]}")
            return b''
        
        # Если прочитали меньше, чем нужно, это может быть конец файла
        if len(data) < frame_size:
            logger.debug(f"Read partial frame: {len(data)}/{frame_size} bytes")
        
        return data
    
    def cleanup(self):
        """Очистить ресурсы"""
        if self.process:
            try:
                self.process.kill()
                self.process.wait()
            except:
                pass
            self.process = None
        
        if self._stdout:
            try:
                self._stdout.close()
            except:
                pass
            self._stdout = None


class FFmpegOpusAudio(AudioSource):
    """Аудио источник из FFmpeg с Opus кодированием"""
    
    def __init__(self, source: str, *, executable: str = 'ffmpeg',
                 before_options: Optional[str] = None, options: Optional[str] = None,
                 bitrate: int = 128):
        self.source = source
        self.executable = executable
        self.before_options = before_options or ''
        self.options = options or f'-c:a libopus -b:a {bitrate}k -f opus'
        self.bitrate = bitrate
        
        self.process: Optional[subprocess.Popen] = None
        self._stdout: Optional[Any] = None
        self._packet_iter: Optional[Iterator[bytes]] = None
        
        super().__init__()
    
    def cleanup(self):
        """Очистить ресурсы"""
        if self.process:
            try:
                self.process.kill()
                self.process.wait()
            except:
                pass
            self.process = None
        
        if self._stdout:
            try:
                self._stdout.close()
            except:
                pass
            self._stdout = None
        
        # Сбросить итератор
        self._packet_iter = None
    
    def _spawn_process(self):
        """Запустить FFmpeg процесс"""
        command = [
            self.executable,
            '-i', self.source,
        ]
        
        if self.before_options:
            command.extend(self.before_options.split())
        
        # FFmpeg с -f opus выдает Ogg контейнер, а не чистые Opus пакеты
        # Используем OggStream для парсинга Ogg контейнера
        # Важно: порядок параметров имеет значение!
        # -re: читать входной файл с реальной скоростью (важно для правильной синхронизации)
        command.extend([
            '-map_metadata', '-1',
            '-f', 'opus',  # Формат вывода - Ogg Opus
            '-c:a', 'libopus',  # Кодек
            '-ar', '48000',  # Sample rate
            '-ac', '2',  # Каналы
            '-b:a', f'{self.bitrate}k',  # Bitrate
            '-loglevel', 'warning',
            '-fec', 'true',  # Forward error correction
            '-packet_loss', '15',  # Expected packet loss %
            'pipe:1'  # Вывод в stdout
        ])
        
        # НЕ добавляем self.options после '-', это вызывает ошибку FFmpeg
        # Все опции должны быть ДО '-'
        
        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self._stdout = self.process.stdout
            logger.info(f"Started FFmpeg Opus process for {self.source}")
            
            # Инициализировать OggStream для парсинга Ogg контейнера
            self._packet_iter = OggStream(self._stdout).iter_packets()
        except FileNotFoundError:
            raise RuntimeError(f"FFmpeg executable '{self.executable}' not found. Please install FFmpeg.")
        except Exception as e:
            raise RuntimeError(f"Failed to start FFmpeg process: {e}")
    
    def read(self) -> bytes:
        """Прочитать Opus данные из Ogg контейнера"""
        if self.process is None:
            self._spawn_process()
        
        if self._packet_iter is None:
            return b''
        
        # Проверяем, завершился ли процесс
        if self.process.poll() is not None:
            # Процесс завершился, проверяем, есть ли еще данные
            try:
                return next(self._packet_iter, b'')
            except StopIteration:
                return b''
        
        try:
            # Используем итератор из OggStream для получения следующего пакета
            return next(self._packet_iter, b'')
        except StopIteration:
            return b''
        except Exception as e:
            logger.error(f"Error reading Opus packet: {e}", exc_info=True)
            return b''
    
    def is_opus(self) -> bool:
        return True
    
    def cleanup(self):
        """Очистить ресурсы"""
        if self.process:
            try:
                self.process.kill()
                self.process.wait()
            except:
                pass
            self.process = None
        
        if self._stdout:
            try:
                self._stdout.close()
            except:
                pass
            self._stdout = None

