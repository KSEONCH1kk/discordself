# Примеры команд

## Базовые команды

### Простые команды

```python
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command(name="hello")
async def hello(ctx):
    await ctx.send(f"Привет, {ctx.author.mention}!")

@bot.command(name="echo")
async def echo(ctx, *, text: str):
    await ctx.send(text)
```

### Команды с аргументами

```python
@bot.command(name="add")
async def add(ctx, a: int, b: int):
    await ctx.send(f"{a} + {b} = {a + b}")

@bot.command(name="multiply")
async def multiply(ctx, a: float, b: float):
    await ctx.send(f"{a} * {b} = {a * b}")

@bot.command(name="repeat")
async def repeat(ctx, count: int, *, text: str):
    if count > 10:
        await ctx.send("❌ Максимум 10 раз!")
        return
    await ctx.send(text * count)
```

## Команды с конвертерами

### UserConverter

```python
from discordself.commands import UserConverter

@bot.command(name="userinfo")
async def userinfo(ctx, user: UserConverter = None):
    target = user or ctx.author
    
    embed = Embed(
        title=f"Информация о {target.username}",
        color=0x3498db
    )
    embed.add_field(name="ID", value=target.id)
    embed.add_field(name="Создан", value=target.created_at)
    embed.add_field(name="Бот", value="Да" if target.bot else "Нет")
    
    await ctx.send(embed=embed)
```

### ChannelConverter

```python
from discordself.commands import ChannelConverter

@bot.command(name="channelinfo")
async def channelinfo(ctx, channel: ChannelConverter = None):
    target = channel or ctx.channel
    
    embed = Embed(
        title=f"Информация о канале {target.name}",
        color=0x3498db
    )
    embed.add_field(name="ID", value=target.id)
    embed.add_field(name="Тип", value=target.type.name)
    if target.topic:
        embed.add_field(name="Тема", value=target.topic)
    
    await ctx.send(embed=embed)
```

### RoleConverter

```python
from discordself.commands import RoleConverter

@bot.command(name="roleinfo")
async def roleinfo(ctx, role: RoleConverter):
    embed = Embed(
        title=f"Информация о роли {role.name}",
        color=role.color if role.color else 0x3498db
    )
    embed.add_field(name="ID", value=role.id)
    embed.add_field(name="Участников", value=len(role.members))
    embed.add_field(name="Упоминаемая", value="Да" if role.mentionable else "Нет")
    
    await ctx.send(embed=embed)
```

## Группы команд

### Базовая группа

```python
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

@mod_group.command(name="mute")
async def mute_command(ctx, user: UserConverter, duration: int = 60):
    await ctx.send(f"Would mute {user.mention} for {duration} seconds")
```

### Вложенные группы

```python
@bot.group(name="config")
async def config_group(ctx):
    """Настройки"""
    if ctx.invoked_subcommand is None:
        await ctx.send("Используйте: config prefix, config language")

@config_group.group(name="prefix")
async def prefix_group(ctx):
    """Настройки префикса"""
    if ctx.invoked_subcommand is None:
        await ctx.send("Используйте: config prefix set, config prefix get")

@prefix_group.command(name="set")
async def prefix_set(ctx, new_prefix: str):
    # Сохранить префикс
    await ctx.send(f"Префикс изменен на: {new_prefix}")

@prefix_group.command(name="get")
async def prefix_get(ctx):
    # Получить префикс
    await ctx.send(f"Текущий префикс: {ctx.prefix}")
```

## Команды с проверками

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
from discordself.checks import has_role

@bot.command(name="admin")
@has_role("Admin")
async def admin_command(ctx):
    await ctx.send("Admin command executed")
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

### Кастомная проверка

```python
from discordself.checks import check

def is_moderator():
    def predicate(ctx):
        if not ctx.guild:
            return False
        member = ctx.guild.get_member(ctx.author.id)
        if not member:
            return False
        return any(role.name in ["Moderator", "Admin"] for role in member.roles)
    return check(predicate)

@bot.command(name="mod")
@is_moderator()
async def mod_command(ctx):
    await ctx.send("Mod command")
```

## Команды с cooldown

### Простой cooldown

```python
from discordself.checks import cooldown

@bot.command(name="limited")
@cooldown(rate=1, per=5.0)
async def limited(ctx):
    await ctx.send("Команда выполнена! Попробуйте снова через 5 секунд.")
```

### Cooldown с лимитом

```python
@bot.command(name="spam")
@cooldown(rate=3, per=10.0)
async def spam(ctx):
    await ctx.send("Команда выполнена!")
```

### Глобальный cooldown

```python
@bot.command(name="global")
@cooldown(rate=1, per=60.0, type=4)
async def global_command(ctx):
    await ctx.send("Глобальная команда")
```

## Команды с опциональными аргументами

```python
@bot.command(name="say")
async def say(ctx, channel: ChannelConverter = None, *, text: str):
    target = channel or ctx.channel
    await target.send(text)

@bot.command(name="kick")
async def kick(ctx, user: UserConverter, *, reason: str = "No reason"):
    await ctx.send(f"Would kick {user.mention} for: {reason}")
```

## Команды с Greedy

```python
from discordself.commands import Greedy

@bot.command(name="add_roles")
async def add_roles(ctx, user: UserConverter, roles: Greedy[RoleConverter]):
    for role in roles:
        await client.add_role(ctx.guild.id, user.id, role.id)
    await ctx.send(f"Добавлено {len(roles)} ролей")
```

## Обработка ошибок

```python
from discordself.exceptions import (
    CommandNotFound,
    MissingRequiredArgument,
    BadArgument,
    CheckFailure,
    CommandOnCooldown
)

@client.event("command_error")
async def on_command_error(ctx, command, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("❌ Команда не найдена!")
    
    elif isinstance(error, MissingRequiredArgument):
        await ctx.send(f"❌ Отсутствует аргумент: {error.param.name}")
    
    elif isinstance(error, BadArgument):
        await ctx.send(f"❌ Неверный аргумент: {error}")
    
    elif isinstance(error, CheckFailure):
        await ctx.send("❌ У вас нет прав для выполнения этой команды!")
    
    elif isinstance(error, CommandOnCooldown):
        await ctx.send(f"⏰ Команда на cooldown! Попробуйте через {error.retry_after:.2f} секунд.")
    
    else:
        await ctx.send(f"❌ Произошла ошибка: {error}")
        import traceback
        traceback.print_exc()
```

