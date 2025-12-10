"""YouTube и URL audio streaming"""

import asyncio
import re
import logging
from typing import Optional, Dict, Any
from .ffmpeg import FFmpegPCMAudio, FFmpegOpusAudio

logger = logging.getLogger(__name__)

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    logger.warning("yt-dlp not available. YouTube streaming will not work. Install with: pip install yt-dlp")


class YouTubeSource(FFmpegPCMAudio):
    """Аудио источник из YouTube"""
    
    def __init__(self, url: str, *, ytdl_options: Optional[Dict] = None, 
                 before_options: Optional[str] = None, options: Optional[str] = None,
                 sample_rate: int = 48000, channels: int = 2):
        if not YT_DLP_AVAILABLE:
            raise RuntimeError("yt-dlp is required for YouTube streaming. Install with: pip install yt-dlp")
        
        self.url = url
        self.ytdl_options = ytdl_options or {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'opus',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }
        
        # Получить URL аудио потока
        self.audio_url = self._get_audio_url()
        
        # Использовать FFmpeg для воспроизведения
        super().__init__(
            self.audio_url,
            before_options=before_options or '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            options=options,
            sample_rate=sample_rate,
            channels=channels
        )
    
    def _get_audio_url(self) -> str:
        """Получить URL аудио потока из YouTube"""
        ydl = yt_dlp.YoutubeDL(self.ytdl_options)
        
        try:
            info = ydl.extract_info(self.url, download=False)
            
            if 'entries' in info:
                # Плейлист - взять первый элемент
                info = info['entries'][0]
            
            # Получить URL
            if 'url' in info:
                return info['url']
            elif 'formats' in info:
                # Найти лучший аудио формат
                for format in info['formats']:
                    if format.get('acodec') != 'none' and format.get('vcodec') == 'none':
                        return format['url']
            
            raise RuntimeError("Could not extract audio URL from YouTube video")
        
        except Exception as e:
            logger.error(f"Failed to extract YouTube audio URL: {e}")
            raise RuntimeError(f"Failed to get YouTube audio URL: {e}")


class URLSource(FFmpegPCMAudio):
    """Аудио источник из URL"""
    
    def __init__(self, url: str, *, before_options: Optional[str] = None,
                 options: Optional[str] = None, sample_rate: int = 48000, channels: int = 2):
        # Проверить, является ли URL YouTube
        youtube_pattern = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        
        if youtube_pattern.match(url):
            # Использовать YouTubeSource
            raise ValueError("Use YouTubeSource for YouTube URLs")
        
        # Использовать FFmpeg для прямого URL
        super().__init__(
            url,
            before_options=before_options or '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            options=options,
            sample_rate=sample_rate,
            channels=channels
        )


async def create_yt_source(url: str, **kwargs) -> YouTubeSource:
    """Создать YouTube источник (async wrapper)"""
    return YouTubeSource(url, **kwargs)


async def create_url_source(url: str, **kwargs) -> URLSource:
    """Создать URL источник (async wrapper)"""
    return URLSource(url, **kwargs)

