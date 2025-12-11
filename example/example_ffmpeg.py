"""Пример использования FFmpeg для воспроизведения аудио"""

import asyncio
import logging
from discordself import Client, Intents
from discordself.voice import VoiceClient
from discordself.ffmpeg import FFmpegPCMAudio, FFmpegOpusAudio

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
    print(f"Бот готов: {client.user}")


async def play_audio_file(guild_id, channel_id, filename: str):
    """Воспроизвести аудио файл через FFmpeg"""
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
            print(f"Ошибка при получении канала: {e}")
            import traceback
            traceback.print_exc()
            return
    
    if not channel:
        print(f"Канал {channel_id} не найден")
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
                print(f"Ошибка при получении guild: {e}")
                return
    
    # Проверить тип канала
    from discordself.enums import ChannelType
    if channel.type not in (ChannelType.GUILD_VOICE, ChannelType.GUILD_STAGE_VOICE):
        print(f"Канал не является голосовым каналом (тип: {channel.type})")
        return
    
    print(f"Канал готов: {channel.name}, Guild: {channel.guild.name if channel.guild else 'None'}")
    
    # Подключиться к голосовому каналу
    voice = VoiceClient(client, channel)
    await voice.connect()
    
    print(f"Подключен к {channel.name}")
    
    # Дождаться готовности voice client
    print("Ожидание готовности voice client...")
    timeout = 10.0
    import time
    start_time = time.time()
    while not voice.ready and (time.time() - start_time) < timeout:
        await asyncio.sleep(0.1)
    
    if not voice.ready:
        print("Voice client не готов после таймаута")
        await voice.disconnect()
        return
    
    print("Voice client готов!")
    
    try:
        # Использовать FFmpegOpusAudio вместо FFmpegPCMAudio, так как opuslib не работает
        # FFmpeg будет кодировать в Opus напрямую
        source = FFmpegOpusAudio(
            filename,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            bitrate=128
        )
        
        # Воспроизвести
        await voice.play(source)
        print("Воспроизведение начато")
        
        # Ждать окончания
        while voice.is_playing():
            await asyncio.sleep(0.1)
        
        print("Воспроизведение завершено")
    
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await voice.disconnect()


async def play_opus_file(guild_id, channel_id, filename: str):
    """Воспроизвести Opus файл через FFmpeg"""
    # Конвертировать в int если переданы строки
    guild_id = int(guild_id)
    channel_id = int(channel_id)
    
    print(f"Поиск канала: guild_id={guild_id}, channel_id={channel_id}")
    
    # Попробовать получить из кэша
    channel = client.get_channel(channel_id)
    
    # Если не найден, получить через HTTP
    if not channel:
        print("Канал не в кэше, получаем через HTTP...")
        try:
            channel = await client.fetch_channel(channel_id)
            print(f"Получен канал через HTTP: {channel.name}")
        except Exception as e:
            print(f"Ошибка при получении канала: {e}")
            return
    
    if not channel:
        print(f"Канал {channel_id} не найден")
        return
    
    voice = VoiceClient(client, channel)
    await voice.connect()
    
    try:
        # Создать FFmpeg источник (Opus)
        source = FFmpegOpusAudio(
            filename,
            bitrate=128
        )
        
        await voice.play(source)
        print("Воспроизведение Opus файла начато")
        
        while voice.is_playing():
            await asyncio.sleep(0.1)
        
        print("Воспроизведение завершено")
    
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await voice.disconnect()


async def main():
    async with client:
        print("Бот запущен!")
        
        # Примеры использования:
        await play_audio_file("1400425075240472596", "1400430839397093386", "music1.mp3")
        
        await asyncio.sleep(3600 * 24)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

