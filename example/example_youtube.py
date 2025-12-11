"""Пример использования YouTube и URL streaming с улучшенным поиском канала"""

import asyncio
import logging
from discordself import Client, Intents
from discordself.voice import VoiceClient
from discordself.youtube import YouTubeSource, URLSource, create_yt_source
from discordself.commands import Bot

# Включить логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

client = Client(
    token="MTQ0MzIzNzUyNTE0MDU0MTQ2MQ.Gq8rd-.ratCR_X2bK2gpNAwpMFCjiRNeRkMgrcBflipL8",
    intents=Intents.GUILDS | Intents.GUILD_VOICE_STATES
)


@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")


async def play_youtube(guild_id, channel_id, url: str):
    """Воспроизвести YouTube видео"""
    # Конвертировать в int если переданы строки
    guild_id = int(guild_id)
    channel_id = int(channel_id)
    
    print(f"Поиск канала: guild_id={guild_id}, channel_id={channel_id}")
    print(f"Каналы в кэше: {list(client.channels.keys())}")
    
    # Попробовать получить из кэша
    channel = client.get_channel(channel_id)
    print(f"Канал из кэша: {channel}")
    
    # Если не найден, получить через HTTP
    if not channel:
        print("🔍 Канал не в кэше, получаем через HTTP...")
        try:
            channel = await client.fetch_channel(channel_id)
            print(f"Получен канал через HTTP: {channel.name} (ID: {channel.id}, Type: {channel.type})")
        except Exception as e:
            print(f"❌ Ошибка при получении канала: {e}")
            import traceback
            traceback.print_exc()
            return
    
    if not channel:
        print(f"❌ Канал {channel_id} не найден")
        return
    
    # Проверить, что канал имеет guild
    if not channel.guild:
        print(f"Канал не имеет guild, пытаемся получить guild из данных канала...")
        # Если guild не установлен, попробовать получить его из guild_id
        if guild_id:
            try:
                guild = await client.fetch_guild(guild_id)
                channel.guild = guild
                print(f"Guild установлен: {guild.name}")
            except Exception as e:
                print(f"❌ Ошибка при получении guild: {e}")
                return
    
    # Проверить тип канала
    from discordself.enums import ChannelType
    if channel.type not in (ChannelType.GUILD_VOICE, ChannelType.GUILD_STAGE_VOICE):
        print(f"❌ Канал не является голосовым каналом (тип: {channel.type})")
        return
    
    print(f"✅ Канал готов: {channel.name}, Guild: {channel.guild.name if channel.guild else 'None'}")
    
    # Подключиться к голосовому каналу
    voice = VoiceClient(client, channel)
    await voice.connect()
    
    print(f"✅ Подключен к {channel.name}")
    
    # Дождаться готовности voice client
    print("⏳ Ожидание готовности voice client...")
    timeout = 10.0
    import time
    start_time = time.time()
    while not voice.ready and (time.time() - start_time) < timeout:
        await asyncio.sleep(0.1)
    
    if not voice.ready:
        print("❌ Voice client не готов после таймаута")
        await voice.disconnect()
        return
    
    print("✅ Voice client готов!")
    
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


async def play_url(guild_id, channel_id, url: str):
    """Воспроизвести аудио из URL"""
    # Конвертировать в int если переданы строки
    guild_id = int(guild_id)
    channel_id = int(channel_id)
    
    print(f"Поиск канала: guild_id={guild_id}, channel_id={channel_id}")
    print(f"Каналы в кэше: {list(client.channels.keys())}")
    
    # Попробовать получить из кэша
    channel = client.get_channel(channel_id)
    print(f"Канал из кэша: {channel}")
    
    # Если не найден, получить через HTTP
    if not channel:
        print("🔍 Канал не в кэше, получаем через HTTP...")
        try:
            channel = await client.fetch_channel(channel_id)
            print(f"Получен канал через HTTP: {channel.name} (ID: {channel.id}, Type: {channel.type})")
        except Exception as e:
            print(f"❌ Ошибка при получении канала: {e}")
            import traceback
            traceback.print_exc()
            return
    
    if not channel:
        print(f"❌ Канал {channel_id} не найден")
        return
    
    # Проверить, что канал имеет guild
    if not channel.guild:
        print(f"Канал не имеет guild, пытаемся получить guild из данных канала...")
        if guild_id:
            try:
                guild = await client.fetch_guild(guild_id)
                channel.guild = guild
                print(f"Guild установлен: {guild.name}")
            except Exception as e:
                print(f"❌ Ошибка при получении guild: {e}")
                return
    
    # Проверить тип канала
    from discordself.enums import ChannelType
    if channel.type not in (ChannelType.GUILD_VOICE, ChannelType.GUILD_STAGE_VOICE):
        print(f"❌ Канал не является голосовым каналом (тип: {channel.type})")
        return
    
    print(f"✅ Канал готов: {channel.name}, Guild: {channel.guild.name if channel.guild else 'None'}")
    
    # Подключиться к голосовому каналу
    voice = VoiceClient(client, channel)
    await voice.connect()
    
    print(f"✅ Подключен к {channel.name}")
    
    # Дождаться готовности voice client
    print("⏳ Ожидание готовности voice client...")
    timeout = 10.0
    import time
    start_time = time.time()
    while not voice.ready and (time.time() - start_time) < timeout:
        await asyncio.sleep(0.1)
    
    if not voice.ready:
        print("❌ Voice client не готов после таймаута")
        await voice.disconnect()
        return
    
    print("✅ Voice client готов!")
    
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
        import traceback
        traceback.print_exc()
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
        
        # Дождаться готовности
        timeout = 10.0
        import time
        start_time = time.time()
        while not voice.ready and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.1)
        
        if not voice.ready:
            await ctx.send("❌ Voice client не готов")
            await voice.disconnect()
            return
        
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
        
        # Примеры использования:
        # await play_youtube("1400425075240472596", "1400430839397093386", "https://www.youtube.com/watch?v=...")
        #await play_youtube("1400425075240472596", "1400430839397093386", "https://www.youtube.com/watch?v=WQ8KruqOz0s")
        await play_url("1400425075240472596", "1400430839397093386", "https://rus.hitmotop.com/get/music/20230227/Shadrow_-_Never_Be_Alone_FNaF_4_Song_75510820.mp3")
        
        await asyncio.sleep(3600 * 24)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())