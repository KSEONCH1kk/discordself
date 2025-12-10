"""Пример использования системы команд"""

import asyncio
from discordself import Client, Intents
from discordself.commands import Bot, Context
from discordself.cogs import Cog, command, listener
from discordself.checks import guild_only, has_permissions


# Создать клиент
client = Client(
    token="YOUR_TOKEN_HERE",
    intents=Intents.GUILDS | Intents.GUILD_MESSAGES | Intents.MESSAGE_CONTENT
)

# Создать Bot с командами
bot = Bot(client, command_prefix="!")


# Пример 1: Простая команда
@bot.command(name="ping")
async def ping_command(ctx: Context):
    """Проверка работы бота"""
    await ctx.send("🏓 Pong!")


# Пример 2: Команда с аргументами
@bot.command(name="echo")
async def echo_command(ctx: Context, *, message: str):
    """Повторить сообщение"""
    await ctx.send(message)


# Пример 3: Команда с типами
@bot.command(name="add")
async def add_command(ctx: Context, a: int, b: int):
    """Сложить два числа"""
    await ctx.send(f"{a} + {b} = {a + b}")


# Пример 4: Команда с проверками
@bot.command(name="kick", checks=[guild_only()])
async def kick_command(ctx: Context, user: str, *, reason: str = "No reason"):
    """Кикнуть пользователя (пример)"""
    await ctx.send(f"Would kick {user} for: {reason}")


# Пример 5: Группа команд
@bot.group(name="mod")
async def mod_group(ctx: Context):
    """Модераторские команды"""
    if ctx.invoked_subcommand is None:
        await ctx.send("Используйте подкоманды: ban, kick, mute")


@mod_group.command(name="ban")
async def ban_command(ctx: Context, user: str):
    """Забанить пользователя"""
    await ctx.send(f"Would ban {user}")


# Пример 6: Cog
class AdminCog(Cog):
    """Cog с админ командами"""
    
    def __init__(self, bot):
        super().__init__(bot)
    
    @command(name="shutdown")
    async def shutdown_command(self, ctx: Context):
        """Выключить бота"""
        await ctx.send("Выключаюсь...")
        await self.bot.client.close()
    
    @listener("ready")
    async def on_ready(self):
        print("AdminCog загружен!")


# Загрузить Cog
bot.cog_manager = bot.cog_manager if hasattr(bot, 'cog_manager') else None
if not bot.cog_manager:
    from discordself.cogs import CogManager
    bot.cog_manager = CogManager(bot)

bot.cog_manager.add_cog(AdminCog(bot))


# Пример 7: Использование listeners
@client.listen("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")


@client.listen("message", priority=1)
async def on_message_high_priority(message):
    """Высокоприоритетный обработчик"""
    if message.content.startswith("!"):
        print(f"Команда обнаружена: {message.content}")


async def main():
    async with client:
        print("🚀 Бот запущен!")
        await asyncio.sleep(3600 * 24)


if __name__ == "__main__":
    asyncio.run(main())

