# Система команд

DiscordSelf предоставляет полнофункциональную систему команд, аналогичную discord.py.

## Основы

### Создание бота с командами

```python
from discordself import Client, Intents
from discordself.commands import Bot

client = Client(
    token="YOUR_TOKEN",
    intents=Intents.GUILD_MESSAGES | Intents.MESSAGE_CONTENT
)

bot = Bot(client, command_prefix="!")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong!")

async def main():
    async with client:
        await asyncio.sleep(3600)

asyncio.run(main())
```

### Базовые команды

```python
@bot.command(name="hello")
async def hello(ctx):
    await ctx.send(f"Привет, {ctx.author.mention}!")

@bot.command(name="echo")
async def echo(ctx, *, text):
    await ctx.send(text)
```

## Парсинг аргументов

### Типы аргументов

```python
@bot.command(name="add")
async def add(ctx, a: int, b: int):
    await ctx.send(f"{a} + {b} = {a + b}")

@bot.command(name="multiply")
async def multiply(ctx, a: float, b: float):
    await ctx.send(f"{a} * {b} = {a * b}")

@bot.command(name="toggle")
async def toggle(ctx, value: bool):
    await ctx.send(f"Value: {value}")
```

### Конвертеры

```python
from discordself.commands import UserConverter, ChannelConverter, RoleConverter

@bot.command(name="userinfo")
async def userinfo(ctx, user: UserConverter):
    await ctx.send(f"User: {user.username} (ID: {user.id})")

@bot.command(name="channelinfo")
async def channelinfo(ctx, channel: ChannelConverter):
    await ctx.send(f"Channel: {channel.name} (ID: {channel.id})")

@bot.command(name="roleinfo")
async def roleinfo(ctx, role: RoleConverter):
    await ctx.send(f"Role: {role.name} (ID: {role.id})")
```

### Опциональные аргументы

```python
@bot.command(name="say")
async def say(ctx, channel: ChannelConverter = None, *, text):
    target = channel or ctx.channel
    await target.send(text)
```

### Значения по умолчанию

```python
@bot.command(name="kick")
async def kick(ctx, user: UserConverter, *, reason: str = "No reason"):
    await ctx.send(f"Would kick {user.mention} for: {reason}")
```

## Группы команд

```python
from discordself.commands import CommandGroup

@bot.group(name="mod")
async def mod_group(ctx):
    """Команды модерации"""
    if ctx.invoked_subcommand is None:
        await ctx.send("Используйте подкоманды: ban, kick, mute")

@mod_group.command(name="ban")
async def ban_command(ctx, user: UserConverter, *, reason: str = "No reason"):
    await ctx.send(f"Would ban {user.mention} for: {reason}")

@mod_group.command(name="kick")
async def kick_command(ctx, user: UserConverter, *, reason: str = "No reason"):
    await ctx.send(f"Would kick {user.mention} for: {reason}")
```

## Checks

### Проверка прав

```python
from discordself.checks import has_permissions
from discordself.permissions import Permissions

@bot.command(name="ban")
@has_permissions(Permissions.BAN_MEMBERS)
async def ban(ctx, user: UserConverter):
    await ctx.send(f"Banned {user.mention}")
```

### Проверка ролей

```python
from discordself.checks import has_role, has_any_role

@bot.command(name="admin")
@has_role("Admin")
async def admin_command(ctx):
    await ctx.send("Admin command executed")

@bot.command(name="mod")
@has_any_role("Moderator", "Admin")
async def mod_command(ctx):
    await ctx.send("Mod command executed")
```

### Проверка владельца

```python
from discordself.checks import is_owner

@bot.command(name="shutdown")
@is_owner()
async def shutdown(ctx):
    await ctx.send("Shutting down...")
    await ctx.bot.client.close()
```

### Проверка канала

```python
from discordself.checks import guild_only, dm_only

@bot.command(name="server")
@guild_only()
async def server_command(ctx):
    await ctx.send(f"Server: {ctx.guild.name}")

@bot.command(name="dm")
@dm_only()
async def dm_command(ctx):
    await ctx.send("This is a DM!")
```

### Кастомные проверки

```python
from discordself.checks import check

def is_admin():
    def predicate(ctx):
        if not ctx.guild:
            return False
        member = ctx.guild.get_member(ctx.author.id)
        if not member:
            return False
        return any(role.name == "Admin" for role in member.roles)
    return check(predicate)

@bot.command(name="admin")
@is_admin()
async def admin_command(ctx):
    await ctx.send("Admin command")
```

## Cooldowns

### Простой cooldown

```python
from discordself.checks import cooldown

@bot.command(name="limited")
@cooldown(rate=1, per=5.0)  # 1 раз в 5 секунд
async def limited_command(ctx):
    await ctx.send("Команда выполнена! Попробуйте снова через 5 секунд.")
```

### Cooldown с лимитом использований

```python
@bot.command(name="spam")
@cooldown(rate=3, per=10.0)  # 3 раза в 10 секунд
async def spam_command(ctx):
    await ctx.send("Команда выполнена!")
```

### Глобальный cooldown

```python
@bot.command(name="global")
@cooldown(rate=1, per=60.0, type=4)  # Глобальный: 1 раз в минуту
async def global_command(ctx):
    await ctx.send("Глобальная команда выполнена!")
```

### Обработка ошибок cooldown

```python
from discordself.exceptions import CommandOnCooldown

@client.event("command_error")
async def on_command_error(ctx, command, error):
    if isinstance(error, CommandOnCooldown):
        await ctx.send(f"⏰ Команда на cooldown! Попробуйте через {error.retry_after:.2f} секунд.")
    else:
        await ctx.send(f"❌ Ошибка: {error}")
```

## Context

`Context` предоставляет доступ к информации о команде и окружении.

### Атрибуты

- `message` (Message): Сообщение, вызвавшее команду
- `author` (User): Автор сообщения
- `channel` (Channel): Канал, где была вызвана команда
- `guild` (Guild, optional): Гильдия
- `bot` (Bot): Экземпляр бота
- `command` (Command): Команда
- `prefix` (str): Префикс команды
- `args` (List[str]): Аргументы команды

### Методы

```python
@bot.command(name="info")
async def info(ctx):
    # Отправить сообщение
    await ctx.send("Hello!")
    
    # Отправить embed
    embed = Embed(title="Info", description="Information")
    await ctx.send(embed=embed)
    
    # Получить информацию
    print(f"Author: {ctx.author}")
    print(f"Channel: {ctx.channel}")
    print(f"Guild: {ctx.guild}")
```

## Help команды

### Встроенная help команда

```python
from discordself.help import DefaultHelpCommand

bot = Bot(client, command_prefix="!", help_command=DefaultHelpCommand())
```

### Кастомная help команда

```python
from discordself.help import HelpCommand

class MyHelpCommand(HelpCommand):
    async def send_bot_help(self, ctx):
        embed = Embed(title="Help", description="Available commands:")
        for command in ctx.bot.commands.values():
            embed.add_field(
                name=command.name,
                value=command.description,
                inline=False
            )
        await ctx.send(embed=embed)

bot = Bot(client, command_prefix="!", help_command=MyHelpCommand())
```

## Обработка ошибок

```python
@client.event("command_error")
async def on_command_error(ctx, command, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("Команда не найдена!")
    elif isinstance(error, MissingRequiredArgument):
        await ctx.send(f"Отсутствует аргумент: {error.param.name}")
    elif isinstance(error, BadArgument):
        await ctx.send(f"Неверный аргумент: {error}")
    elif isinstance(error, CheckFailure):
        await ctx.send("У вас нет прав для выполнения этой команды!")
    elif isinstance(error, CommandOnCooldown):
        await ctx.send(f"Команда на cooldown! Попробуйте через {error.retry_after:.2f} секунд.")
    else:
        await ctx.send(f"Произошла ошибка: {error}")
        import traceback
        traceback.print_exc()
```

## Best Practices

1. **Используйте type hints** для автоматического парсинга аргументов
2. **Добавляйте проверки** для защиты команд
3. **Обрабатывайте ошибки** для лучшего UX
4. **Используйте cooldowns** для предотвращения спама
5. **Документируйте команды** через docstrings

