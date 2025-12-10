"""Пример использования YouTube и URL streaming"""

import asyncio
from discordself import Client, Intents
from discordself.voice import VoiceClient
from discordself.youtube import YouTubeSource, URLSource, create_yt_source
from discordself.commands import Bot

client = Client(
    token="YOUR_TOKEN_HERE",
    intents=Intents.GUILDS | Intents.GUILD_VOICE_STATES
)


@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")


async def play_youtube(guild_id: int, channel_id: int, url: str):
    """Воспроизвести YouTube видео"""
    guild = await client.fetch_guild(guild_id)
    channel = client.get_channel(channel_id)
    
    if not channel:
        print("❌ Канал не найден")
        return
    
    voice = VoiceClient(client, channel)
    await voice.connect()
    
    print(f"✅ Подключен к {channel.name}")
    
    try:
        # Создать YouTube источник
        source = YouTubeSource(
            url,
            ytdl_options={
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'opus',
            }
        )
        
        print(f"🎵 Загрузка YouTube видео: {url}")
        
        # Воспроизвести
        await voice.play(source)
        print("🎵 Воспроизведение начато")
        
        # Ждать окончания
        while voice.is_playing():
            await asyncio.sleep(0.1)
        
        print("✅ Воспроизведение завершено")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await voice.disconnect()


async def play_url(guild_id: int, channel_id: int, url: str):
    """Воспроизвести аудио из URL"""
    guild = await client.fetch_guild(guild_id)
    channel = client.get_channel(channel_id)
    
    if not channel:
        print("❌ Канал не найден")
        return
    
    voice = VoiceClient(client, channel)
    await voice.connect()
    
    try:
        # Создать URL источник
        source = URLSource(url)
        
        print(f"🎵 Воспроизведение из URL: {url}")
        
        await voice.play(source)
        print("🎵 Воспроизведение начато")
        
        while voice.is_playing():
            await asyncio.sleep(0.1)
        
        print("✅ Воспроизведение завершено")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await voice.disconnect()


# Пример с командами
bot = Bot(client, command_prefix="!")


@bot.command(name="play")
async def play_command(ctx, url: str):
    """Воспроизвести YouTube или URL"""
    if not ctx.guild:
        await ctx.send("❌ Команда работает только на сервере")
        return
    
    channel = ctx.author.voice.channel if hasattr(ctx.author, 'voice') and ctx.author.voice else None
    if not channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    await ctx.send(f"🎵 Загрузка: {url}")
    
    try:
        voice = VoiceClient(client, channel)
        await voice.connect()
        
        # Определить тип URL
        if "youtube.com" in url or "youtu.be" in url:
            source = YouTubeSource(url)
        else:
            source = URLSource(url)
        
        await voice.play(source)
        await ctx.send("✅ Воспроизведение начато")
        
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")


async def main():
    async with client:
        print("🚀 Бот запущен!")
        print("Попробуйте команду: !play <youtube_url или audio_url>")
        
        # Или используйте напрямую:
        # await play_youtube(GUILD_ID, CHANNEL_ID, "https://www.youtube.com/watch?v=...")
        # await play_url(GUILD_ID, CHANNEL_ID, "https://example.com/audio.mp3")
        
        await asyncio.sleep(3600 * 24)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

