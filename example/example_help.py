"""Пример использования Help Command"""

import asyncio
from discordself import Client, Intents
from discordself.commands import Bot
from discordself.help import setup_help_command, DefaultHelpCommand

client = Client(
    token="YOUR_TOKEN_HERE",
    intents=Intents.GUILDS | Intents.GUILD_MEMBERS
)

bot = Bot(client, command_prefix="!")

# Настроить help команду
setup_help_command(bot)


@bot.command(name="ping", description="Проверить задержку бота")
async def ping(ctx):
    """Проверить задержку бота"""
    await ctx.send("🏓 Pong!")


@bot.command(name="echo", description="Повторить сообщение")
async def echo(ctx, *, message: str):
    """Повторить ваше сообщение"""
    await ctx.send(message)


@bot.command(name="userinfo", description="Информация о пользователе")
async def user_info(ctx):
    """Показать информацию о пользователе"""
    user = ctx.author
    await ctx.send(f"Пользователь: {user.username}\nID: {user.id}")


@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")
    print("Попробуйте команды:")
    print("  !help - показать все команды")
    print("  !help ping - показать справку по команде ping")


async def main():
    async with client:
        await asyncio.sleep(3600 * 24)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

