# Голосовые функции

DiscordSelf поддерживает полную работу с голосовыми каналами Discord.

## Подключение к голосовому каналу

### Базовое подключение

```python
from discordself.voice import VoiceClient

# Получить голосовой канал
channel = await client.fetch_channel(channel_id)

# Подключиться
voice_client = await channel.connect()
```

### Использование функции connect_to_voice

```python
from discordself.voice import connect_to_voice

voice_client = await connect_to_voice(client, channel_id)
```

## Воспроизведение аудио

### Воспроизведение файла

```python
from discordself.ffmpeg import FFmpegPCMAudio

# Подключиться к каналу
voice_client = await channel.connect()

# Воспроизвести файл
source = FFmpegPCMAudio("music.mp3")
voice_client.play(source)

# Ожидать окончания
while voice_client.is_playing():
    await asyncio.sleep(1)
```

### Воспроизведение с Opus

```python
from discordself.ffmpeg import FFmpegOpusAudio

source = FFmpegOpusAudio("music.mp3")
voice_client.play(source)
```

### Воспроизведение YouTube

```python
from discordself.youtube import YouTubeSource

# Создать источник из YouTube URL
source = await YouTubeSource.from_url("https://www.youtube.com/watch?v=...")
voice_client.play(source)
```

### Воспроизведение из URL

```python
from discordself.youtube import URLSource

source = await URLSource.from_url("https://example.com/audio.mp3")
voice_client.play(source)
```

## Управление воспроизведением

### Пауза и возобновление

```python
# Пауза
voice_client.pause()

# Возобновление
voice_client.resume()
```

### Остановка

```python
# Остановить воспроизведение
voice_client.stop()
```

### Проверка состояния

```python
if voice_client.is_playing():
    print("Воспроизведение...")
elif voice_client.is_paused():
    print("На паузе")
else:
    print("Остановлено")
```

### Callback после окончания

```python
def after_playing(error):
    if error:
        print(f"Ошибка: {error}")
    else:
        print("Воспроизведение завершено")

source = FFmpegPCMAudio("music.mp3")
voice_client.play(source, after=after_playing)
```

## Аудио эффекты

### Изменение громкости

```python
from discordself.audio_source import VolumeTransformer

source = FFmpegPCMAudio("music.mp3")
# Увеличить громкость в 2 раза
volume = VolumeTransformer(source, volume=2.0)
voice_client.play(volume)
```

### Фильтры

```python
from discordself.audio_source import LowPassFilter, FilteredAudioSource

source = FFmpegPCMAudio("music.mp3")
# Применить low-pass фильтр
filtered = FilteredAudioSource(source, LowPassFilter(cutoff=3000))
voice_client.play(filtered)
```

## Запись аудио

### Запись в файл

```python
from discordself.recording import RecordingVoiceClient

# Подключиться с записью
voice_client = await RecordingVoiceClient.connect(channel)

# Начать запись
voice_client.start_recording("output.pcm")

# Остановить запись
voice_client.stop_recording()
```

### Запись в PCM файл

```python
from discordself.recording import PCMFileSink

sink = PCMFileSink("output.pcm")
voice_client.start_recording(sink)
```

## Отключение

```python
# Отключиться от голосового канала
await voice_client.disconnect()
```

## Примеры

### Музыкальный бот

```python
from discordself.voice import VoiceClient
from discordself.ffmpeg import FFmpegOpusAudio
from discordself.commands import Bot

bot = Bot(client, command_prefix="!")

@bot.command(name="play")
async def play(ctx, url: str):
    # Проверить, что пользователь в голосовом канале
    if not ctx.author.voice:
        await ctx.send("Вы должны быть в голосовом канале!")
        return
    
    channel = ctx.author.voice.channel
    
    # Подключиться к каналу
    if not ctx.guild.voice_client:
        voice_client = await channel.connect()
    else:
        voice_client = ctx.guild.voice_client
    
    # Воспроизвести
    source = await YouTubeSource.from_url(url)
    voice_client.play(source)
    await ctx.send(f"Воспроизведение: {url}")

@bot.command(name="stop")
async def stop(ctx):
    if ctx.guild.voice_client:
        ctx.guild.voice_client.stop()
        await ctx.send("Остановлено")

@bot.command(name="disconnect")
async def disconnect(ctx):
    if ctx.guild.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Отключено")
```

### Очередь воспроизведения

```python
class MusicQueue:
    def __init__(self, voice_client):
        self.voice_client = voice_client
        self.queue = []
        self.current = None
    
    def add(self, source):
        self.queue.append(source)
        if not self.voice_client.is_playing():
            self.play_next()
    
    def play_next(self):
        if self.queue:
            self.current = self.queue.pop(0)
            self.voice_client.play(self.current, after=self._after_playing)
        else:
            self.current = None
    
    def _after_playing(self, error):
        if error:
            print(f"Ошибка: {error}")
        self.play_next()

# Использование
queue = MusicQueue(voice_client)
queue.add(FFmpegOpusAudio("song1.mp3"))
queue.add(FFmpegOpusAudio("song2.mp3"))
```

## Troubleshooting

### Проблемы с Opus

Если возникают проблемы с Opus, убедитесь, что `opus.dll` находится в доступном месте:

```python
# Windows: поместите opus.dll в папку с проектом или в PATH
# Linux: установите libopus через пакетный менеджер
```

### Проблемы с FFmpeg

Убедитесь, что FFmpeg установлен и доступен в PATH:

```bash
ffmpeg -version
```

### Проблемы с задержкой

Для уменьшения задержки используйте `FFmpegOpusAudio` вместо `FFmpegPCMAudio`:

```python
# ✅ Лучше для производительности
source = FFmpegOpusAudio("music.mp3")

# ⚠️ Может быть медленнее
source = FFmpegPCMAudio("music.mp3")
```

