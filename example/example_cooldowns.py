"""Пример использования Cooldowns"""

import asyncio
from discordself import Client, Intents
from discordself.commands import Bot
from discordself.checks import cooldown
from discordself.exceptions import CommandOnCooldown

client = Client(
    token="YOUR_TOKEN_HERE",
    intents=Intents.GUILDS
)

bot = Bot(client, command_prefix="!")


@bot.command(name="limited")
@cooldown(rate=1, per=5.0)  # 1 раз в 5 секунд
async def limited_command(ctx):
    """Команда с ограничением использования"""
    await ctx.send("✅ Команда выполнена! Попробуйте снова через 5 секунд.")


@bot.command(name="spam")
@cooldown(rate=3, per=10.0)  # 3 раза в 10 секунд
async def spam_command(ctx):
    """Команда с ограничением 3 раза в 10 секунд"""
    await ctx.send("✅ Команда выполнена!")


@bot.command(name="global_cooldown")
@cooldown(rate=1, per=60.0, type=4)  # Глобальный cooldown: 1 раз в минуту
async def global_command(ctx):
    """Команда с глобальным cooldown"""
    await ctx.send("✅ Глобальная команда выполнена!")


# Обработка ошибки cooldown
@client.event("command_error")
async def on_command_error(ctx, command, error):
    if isinstance(error, CommandOnCooldown):
        await ctx.send(f"⏰ Команда на cooldown! Попробуйте через {error.retry_after:.2f} секунд.")
    else:
        await ctx.send(f"❌ Ошибка: {error}")


@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")
    print("Попробуйте команды:")
    print("  !limited - команда с cooldown 5 секунд")
    print("  !spam - команда с cooldown 3 раза в 10 секунд")


async def main():
    async with client:
        await asyncio.sleep(3600 * 24)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

