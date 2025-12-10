"""Примеры использования Converters"""

import asyncio
from discordself import Client, Intents
from discordself.commands import Bot
from discordself.models import Role, Emoji
from discordself.commands import Greedy, Literal

client = Client(
    token="YOUR_TOKEN_HERE",
    intents=Intents.GUILDS | Intents.GUILD_MEMBERS | Intents.GUILD_EMOJIS_AND_STICKERS
)

bot = Bot(client, command_prefix="!")


@bot.command(name="roleinfo")
async def role_info(ctx, role: Role):
    """Получить информацию о роли"""
    await ctx.send(f"Роль: {role.name}\nID: {role.id}\nЦвет: {role.color}")


@bot.command(name="emojiinfo")
async def emoji_info(ctx, emoji: Emoji):
    """Получить информацию об эмодзи"""
    if emoji:
        await ctx.send(f"Эмодзи: {emoji.name}\nID: {emoji.id}\nАнимированное: {emoji.animated}")
    else:
        await ctx.send("Эмодзи не найдено")


@bot.command(name="assign")
async def assign_role(ctx, role: Role, *members):
    """Назначить роль нескольким участникам"""
    # Greedy позволяет принимать множество аргументов
    from discordself.models import Member
    
    assigned = []
    for member in members:
        if isinstance(member, Member):
            # Здесь должна быть логика назначения роли
            assigned.append(member.display_name if hasattr(member, 'display_name') else str(member))
    
    await ctx.send(f"Роль {role.name} назначена: {', '.join(assigned) if assigned else 'никому'}")


@bot.command(name="mode")
async def set_mode(ctx, mode: Literal("on", "off", "auto")):
    """Установить режим (только on, off или auto)"""
    await ctx.send(f"Режим установлен: {mode}")


@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")


async def main():
    async with client:
        await asyncio.sleep(3600 * 24)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

