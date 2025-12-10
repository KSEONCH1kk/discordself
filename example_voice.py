"""Пример использования Voice поддержки"""

import asyncio
from discordself import Client, Intents
from discordself.voice import VoiceClient, connect_to_voice
from discordself.audio_source import SilenceSource, FileAudioSource


client = Client(
    token="YOUR_TOKEN_HERE",
    intents=Intents.GUILDS | Intents.GUILD_VOICE_STATES
)


@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")


@client.event("voice_state_update")
async def on_voice_state_update(voice_state):
    """Обработка изменений voice state"""
    user = voice_state.user
    channel = voice_state.channel
    if user and channel:
        if voice_state.channel_id:
            print(f"{user} присоединился к {channel.name}")
        else:
            print(f"{user} покинул голосовой канал")


async def join_and_play(guild_id: int, channel_id: int):
    """Пример подключения к голосовому каналу и воспроизведения"""
    guild = await client.fetch_guild(guild_id)
    channel = client.get_channel(channel_id)
    
    if not channel:
        print("❌ Канал не найден")
        return
    
    # Подключиться к голосовому каналу
    voice = VoiceClient(client, channel)
    await voice.connect()
    
    print(f"✅ Подключен к {channel.name}")
    
    # Воспроизвести тишину (пример)
    # Для реального аудио используйте FileAudioSource с Opus файлом
    source = SilenceSource(duration=5.0)  # 5 секунд тишины
    
    try:
        await voice.play(source)
        print("🎵 Воспроизведение начато")
        
        # Ждать окончания
        while voice.is_playing():
            await asyncio.sleep(0.1)
        
        print("✅ Воспроизведение завершено")
    except Exception as e:
        print(f"❌ Ошибка воспроизведения: {e}")
    finally:
        await voice.disconnect()


async def main():
    async with client:
        print("🚀 Бот запущен!")
        
        # Пример подключения к голосовому каналу
        # await join_and_play(GUILD_ID, CHANNEL_ID)
        
        await asyncio.sleep(3600 * 24)


if __name__ == "__main__":
    asyncio.run(main())

