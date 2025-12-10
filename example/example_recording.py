"""Пример использования Recording (запись аудио)"""

import asyncio
from discordself import Client, Intents
from discordself.recording import RecordingVoiceClient, PCMFileSink, FileSink
from discordself.commands import Bot

client = Client(
    token="YOUR_TOKEN_HERE",
    intents=Intents.GUILDS | Intents.GUILD_VOICE_STATES
)


@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")


async def record_audio(guild_id: int, channel_id: int, output_file: str, duration: float = 10.0):
    """Записать аудио из голосового канала"""
    guild = await client.fetch_guild(guild_id)
    channel = client.get_channel(channel_id)
    
    if not channel:
        print("❌ Канал не найден")
        return
    
    # Использовать RecordingVoiceClient
    voice = RecordingVoiceClient(client, channel)
    await voice.connect()
    
    print(f"✅ Подключен к {channel.name}")
    
    try:
        # Создать sink для записи PCM
        sink = PCMFileSink(output_file)
        
        # Добавить sink
        voice.add_sink(sink)
        
        # Начать запись
        await voice.start_recording()
        print(f"🎙️ Запись начата, будет записано {duration} секунд...")
        
        # Записать указанное время
        await asyncio.sleep(duration)
        
        # Остановить запись
        await voice.stop_recording()
        print(f"✅ Запись завершена, сохранена в {output_file}")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await voice.disconnect()


async def record_user_audio(guild_id: int, channel_id: int, user_id: int, output_file: str, duration: float = 10.0):
    """Записать аудио конкретного пользователя"""
    guild = await client.fetch_guild(guild_id)
    channel = client.get_channel(channel_id)
    
    if not channel:
        print("❌ Канал не найден")
        return
    
    voice = RecordingVoiceClient(client, channel)
    await voice.connect()
    
    try:
        # Создать sink только для конкретного пользователя
        sink = PCMFileSink(output_file, user_id=user_id)
        
        voice.add_sink(sink)
        
        await voice.start_recording()
        print(f"🎙️ Запись пользователя {user_id} начата...")
        
        await asyncio.sleep(duration)
        
        await voice.stop_recording()
        print(f"✅ Запись завершена")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await voice.disconnect()


async def record_multiple_users(guild_id: int, channel_id: int, output_dir: str, duration: float = 10.0):
    """Записать аудио нескольких пользователей в разные файлы"""
    guild = await client.fetch_guild(guild_id)
    channel = client.get_channel(channel_id)
    
    if not channel:
        print("❌ Канал не найден")
        return
    
    voice = RecordingVoiceClient(client, channel)
    await voice.connect()
    
    try:
        # Получить список пользователей в канале
        # В реальной реализации нужно получить список из voice states
        user_ids = []  # Здесь должны быть ID пользователей
        
        # Создать sink для каждого пользователя
        sinks = []
        for user_id in user_ids:
            filename = f"{output_dir}/user_{user_id}.pcm"
            sink = PCMFileSink(filename, user_id=user_id)
            voice.add_sink(sink)
            sinks.append(sink)
        
        await voice.start_recording()
        print(f"🎙️ Запись {len(sinks)} пользователей начата...")
        
        await asyncio.sleep(duration)
        
        await voice.stop_recording()
        print(f"✅ Запись завершена, файлы сохранены в {output_dir}")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await voice.disconnect()


# Пример с командами
bot = Bot(client, command_prefix="!")


@bot.command(name="record")
async def record_command(ctx, duration: float = 10.0):
    """Записать аудио из голосового канала"""
    if not ctx.guild:
        await ctx.send("❌ Команда работает только на сервере")
        return
    
    channel = ctx.author.voice.channel if hasattr(ctx.author, 'voice') and ctx.author.voice else None
    if not channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    output_file = f"recording_{ctx.guild.id}_{ctx.channel.id}.pcm"
    
    voice = RecordingVoiceClient(client, channel)
    await voice.connect()
    
    try:
        sink = PCMFileSink(output_file)
        voice.add_sink(sink)
        
        await voice.start_recording()
        await ctx.send(f"🎙️ Запись начата на {duration} секунд...")
        
        await asyncio.sleep(duration)
        
        await voice.stop_recording()
        await ctx.send(f"✅ Запись завершена, сохранена в {output_file}")
    
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")
    finally:
        await voice.disconnect()


async def main():
    async with client:
        print("🚀 Бот запущен!")
        print("Попробуйте команду: !record [длительность]")
        
        # Или используйте напрямую:
        # await record_audio(GUILD_ID, CHANNEL_ID, "recording.pcm", duration=10.0)
        # await record_user_audio(GUILD_ID, CHANNEL_ID, USER_ID, "user_recording.pcm")
        
        await asyncio.sleep(3600 * 24)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

