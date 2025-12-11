# Примеры голосовых функций

## Базовое воспроизведение

### Воспроизведение файла

```python
from discordself.voice import VoiceClient
from discordself.ffmpeg import FFmpegOpusAudio

# Подключиться к каналу
channel = await client.fetch_channel(channel_id)
voice_client = await channel.connect()

# Воспроизвести файл
source = FFmpegOpusAudio("music.mp3")
voice_client.play(source)

# Ожидать окончания
while voice_client.is_playing():
    await asyncio.sleep(1)
```

### Воспроизведение YouTube

```python
from discordself.youtube import YouTubeSource

# Подключиться
voice_client = await channel.connect()

# Воспроизвести YouTube
source = await YouTubeSource.from_url("https://www.youtube.com/watch?v=...")
voice_client.play(source)
```

## Музыкальный бот

```python
from discordself.commands import Bot
from discordself.voice import VoiceClient
from discordself.ffmpeg import FFmpegOpusAudio
from discordself.youtube import YouTubeSource

bot = Bot(client, command_prefix="!")

@bot.command(name="play")
async def play(ctx, url: str):
    # Проверить, что пользователь в голосовом канале
    if not ctx.author.voice:
        await ctx.send("❌ Вы должны быть в голосовом канале!")
        return
    
    channel = ctx.author.voice.channel
    
    # Подключиться
    if not ctx.guild.voice_client:
        voice_client = await channel.connect()
    else:
        voice_client = ctx.guild.voice_client
    
    # Воспроизвести
    try:
        if "youtube.com" in url or "youtu.be" in url:
            source = await YouTubeSource.from_url(url)
        else:
            source = FFmpegOpusAudio(url)
        
        voice_client.play(source)
        await ctx.send(f"🎵 Воспроизведение: {url}")
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")

@bot.command(name="stop")
async def stop(ctx):
    if ctx.guild.voice_client:
        ctx.guild.voice_client.stop()
        await ctx.send("⏹ Остановлено")

@bot.command(name="pause")
async def pause(ctx):
    if ctx.guild.voice_client:
        ctx.guild.voice_client.pause()
        await ctx.send("⏸ На паузе")

@bot.command(name="resume")
async def resume(ctx):
    if ctx.guild.voice_client:
        ctx.guild.voice_client.resume()
        await ctx.send("▶ Возобновлено")

@bot.command(name="disconnect")
async def disconnect(ctx):
    if ctx.guild.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("👋 Отключено")
```

## Очередь воспроизведения

```python
class MusicQueue:
    def __init__(self, voice_client):
        self.voice_client = voice_client
        self.queue = []
        self.current = None
        self.loop = False
    
    def add(self, source):
        self.queue.append(source)
        if not self.voice_client.is_playing():
            self.play_next()
    
    def play_next(self):
        if self.queue:
            self.current = self.queue.pop(0)
            self.voice_client.play(
                self.current,
                after=self._after_playing
            )
        elif self.loop and self.current:
            # Повторить текущий трек
            self.voice_client.play(
                self.current,
                after=self._after_playing
            )
        else:
            self.current = None
    
    def _after_playing(self, error):
        if error:
            print(f"Ошибка воспроизведения: {error}")
        self.play_next()
    
    def skip(self):
        if self.voice_client.is_playing():
            self.voice_client.stop()
    
    def clear(self):
        self.queue.clear()
        if self.voice_client.is_playing():
            self.voice_client.stop()

# Использование
queue = MusicQueue(voice_client)

@bot.command(name="queue")
async def queue_command(ctx, url: str):
    if "youtube.com" in url:
        source = await YouTubeSource.from_url(url)
    else:
        source = FFmpegOpusAudio(url)
    
    queue.add(source)
    await ctx.send(f"✅ Добавлено в очередь: {url}")

@bot.command(name="skip")
async def skip_command(ctx):
    queue.skip()
    await ctx.send("⏭ Пропущено")

@bot.command(name="clear")
async def clear_command(ctx):
    queue.clear()
    await ctx.send("🗑 Очередь очищена")
```

## Запись голоса

```python
from discordself.recording import RecordingVoiceClient

@bot.command(name="record")
async def record_command(ctx):
    if not ctx.author.voice:
        await ctx.send("❌ Вы должны быть в голосовом канале!")
        return
    
    channel = ctx.author.voice.channel
    
    # Подключиться с записью
    voice_client = await RecordingVoiceClient.connect(channel)
    
    # Начать запись
    voice_client.start_recording("output.pcm")
    await ctx.send("🔴 Запись начата!")
    
    # Остановить через 60 секунд
    await asyncio.sleep(60)
    voice_client.stop_recording()
    await ctx.send("⏹ Запись остановлена!")
    await voice_client.disconnect()
```

## Аудио эффекты

```python
from discordself.audio_source import VolumeTransformer, LowPassFilter, FilteredAudioSource

# Изменить громкость
source = FFmpegOpusAudio("music.mp3")
volume = VolumeTransformer(source, volume=1.5)  # Увеличить на 50%
voice_client.play(volume)

# Применить фильтр
source = FFmpegOpusAudio("music.mp3")
filtered = FilteredAudioSource(source, LowPassFilter(cutoff=3000))
voice_client.play(filtered)
```

## Радио бот

```python
class RadioBot:
    def __init__(self, voice_client):
        self.voice_client = voice_client
        self.stations = {
            "rock": "http://stream.rockradio.com:80/",
            "jazz": "http://stream.jazzradio.com:80/",
            "classical": "http://stream.classicalradio.com:80/"
        }
        self.current_station = None
    
    async def play_station(self, station_name):
        if station_name not in self.stations:
            return False
        
        url = self.stations[station_name]
        source = await URLSource.from_url(url)
        self.voice_client.play(source)
        self.current_station = station_name
        return True

radio = RadioBot(voice_client)

@bot.command(name="radio")
async def radio_command(ctx, station: str = None):
    if not station:
        await ctx.send(f"Доступные станции: {', '.join(radio.stations.keys())}")
        return
    
    if await radio.play_station(station):
        await ctx.send(f"📻 Играет: {station}")
    else:
        await ctx.send("❌ Станция не найдена!")
```

