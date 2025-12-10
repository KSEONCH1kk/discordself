"""Пример использования DiscordSelf библиотеки"""

import asyncio
import os
from discordself import Client, Status, Intents

# Получить токен из переменной окружения
TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_TOKEN_HERE")

# Создать клиент с нужными intents для получения сообщений
client = Client(
    token="MTQ0MzIzNzUyNTE0MDU0MTQ2MQ.Gq8rd-.ratCR_X2bK2gpNAwpMFCjiRNeRkMgrcBflipL8",
    intents=Intents.GUILDS | Intents.GUILD_MESSAGES | Intents.DIRECT_MESSAGES | Intents.MESSAGE_CONTENT
)


@client.event("ready")
async def on_ready():
    """Вызывается когда клиент готов"""
    print(f"✅ Logged in as {client.user}")
    print(f"📊 Connected to {len(client.guilds)} guilds")
    
    # Изменить статус
    await client.change_presence(
        status=Status.ONLINE,
        activities=[{
            "name": "DiscordSelf Library",
            "type": 0  # Playing
        }]
    )


@client.event("message")
async def on_message(message):
    """Обработчик новых сообщений"""
    # Игнорировать сообщения от ботов
    if message.author.bot:
        return
    
    # Команда !ping
    if message.content == "!ping":
        await message.channel.send("🏓 Pong!")
    
    # Команда !info
    elif message.content == "!info":
        info = f"""
        **Bot Info:**
        - User: {client.user}
        - Guilds: {len(client.guilds)}
        - Channels: {len(client.channels)}
        """
        await message.channel.send(info)
    
    # Команда !echo
    elif message.content.startswith("!echo "):
        text = message.content[6:]  # Убрать "!echo "
        await message.channel.send(text)


@client.event("guild_join")
async def on_guild_join(guild):
    """Вызывается при присоединении к гильдии"""
    print(f"➕ Joined guild: {guild.name}")


@client.event("guild_remove")
async def on_guild_remove(guild):
    """Вызывается при покидании гильдии"""
    print(f"➖ Left guild: {guild.name if guild else 'Unknown'}")


async def main():
    """Главная функция"""
    try:
        # Запустить клиент
        async with client:
            print("🚀 Client started. Press Ctrl+C to stop.")
            # Работать бесконечно
            await asyncio.sleep(3600 * 24)  # 24 часа
    except KeyboardInterrupt:
        print("\n⏹️  Stopping client...")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

