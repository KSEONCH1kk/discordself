"""Пример использования Audio Effects (Volume, Filters)"""

import asyncio
from discordself import Client, Intents
from discordself.voice import VoiceClient
from discordself.audio_source import (
    VolumeTransformer,
    FilteredAudioSource,
    LowPassFilter,
    SilenceSource
)
from discordself.ffmpeg import FFmpegPCMAudio
from discordself.commands import Bot

client = Client(
    token="YOUR_TOKEN_HERE",
    intents=Intents.GUILDS | Intents.GUILD_VOICE_STATES
)


@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")


async def play_with_volume(guild_id: int, channel_id: int, filename: str, volume: float = 1.0):
    """Воспроизвести аудио с регулировкой громкости"""
    guild = await client.fetch_guild(guild_id)
    channel = client.get_channel(channel_id)
    
    if not channel:
        print("❌ Канал не найден")
        return
    
    voice = VoiceClient(client, channel)
    await voice.connect()
    
    try:
        # Создать базовый источник
        source = FFmpegPCMAudio(filename)
        
        # Применить громкость
        # volume: 0.0 = тишина, 1.0 = нормальная, 2.0 = двойная громкость
        volume_source = VolumeTransformer(source, volume=volume)
        
        print(f"🎵 Воспроизведение с громкостью {volume * 100}%")
        
        await voice.play(volume_source)
        
        while voice.is_playing():
            await asyncio.sleep(0.1)
        
        print("✅ Воспроизведение завершено")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await voice.disconnect()


async def play_with_filter(guild_id: int, channel_id: int, filename: str):
    """Воспроизвести аудио с фильтром"""
    guild = await client.fetch_guild(guild_id)
    channel = client.get_channel(channel_id)
    
    if not channel:
        print("❌ Канал не найден")
        return
    
    voice = VoiceClient(client, channel)
    await voice.connect()
    
    try:
        # Создать базовый источник
        source = FFmpegPCMAudio(filename)
        
        # Применить низкочастотный фильтр (убрать высокие частоты)
        lowpass = LowPassFilter(cutoff=3000.0)  # Отсечка на 3kHz
        filtered_source = FilteredAudioSource(source, lowpass)
        
        print("🎵 Воспроизведение с низкочастотным фильтром")
        
        await voice.play(filtered_source)
        
        while voice.is_playing():
            await asyncio.sleep(0.1)
        
        print("✅ Воспроизведение завершено")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await voice.disconnect()


async def play_with_effects(guild_id: int, channel_id: int, filename: str):
    """Воспроизвести аудио с несколькими эффектами"""
    guild = await client.fetch_guild(guild_id)
    channel = client.get_channel(channel_id)
    
    if not channel:
        print("❌ Канал не найден")
        return
    
    voice = VoiceClient(client, channel)
    await voice.connect()
    
    try:
        # Создать базовый источник
        source = FFmpegPCMAudio(filename)
        
        # Применить громкость
        volume_source = VolumeTransformer(source, volume=1.5)  # 150%
        
        # Применить фильтр
        lowpass = LowPassFilter(cutoff=4000.0)
        filtered_source = FilteredAudioSource(volume_source, lowpass)
        
        print("🎵 Воспроизведение с эффектами (громкость + фильтр)")
        
        await voice.play(filtered_source)
        
        while voice.is_playing():
            await asyncio.sleep(0.1)
        
        print("✅ Воспроизведение завершено")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await voice.disconnect()


# Пример с командами
bot = Bot(client, command_prefix="!")


@bot.command(name="volume")
async def volume_command(ctx, volume: float = 1.0):
    """Воспроизвести аудио с указанной громкостью"""
    if not ctx.guild:
        await ctx.send("❌ Команда работает только на сервере")
        return
    
    channel = ctx.author.voice.channel if hasattr(ctx.author, 'voice') and ctx.author.voice else None
    if not channel:
        await ctx.send("❌ Вы должны быть в голосовом канале")
        return
    
    # Ограничить громкость от 0.0 до 2.0
    volume = max(0.0, min(2.0, volume))
    
    voice = VoiceClient(client, channel)
    await voice.connect()
    
    try:
        source = SilenceSource(duration=5.0)  # 5 секунд тишины для примера
        volume_source = VolumeTransformer(source, volume=volume)
        
        await voice.play(volume_source)
        await ctx.send(f"✅ Воспроизведение с громкостью {volume * 100}%")
    
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")


async def main():
    async with client:
        print("🚀 Бот запущен!")
        print("Попробуйте команды:")
        print("  !volume 1.5 - воспроизвести с громкостью 150%")
        
        # Или используйте напрямую:
        # await play_with_volume(GUILD_ID, CHANNEL_ID, "audio.mp3", volume=1.5)
        # await play_with_filter(GUILD_ID, CHANNEL_ID, "audio.mp3")
        # await play_with_effects(GUILD_ID, CHANNEL_ID, "audio.mp3")
        
        await asyncio.sleep(3600 * 24)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

