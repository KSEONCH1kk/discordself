# Permissions - Права доступа

DiscordSelf предоставляет инструменты для работы с правами доступа Discord.

## Класс Permissions

### Базовое использование

```python
from discordself.permissions import Permissions

# Проверить права
permissions = Permissions.SEND_MESSAGES | Permissions.READ_MESSAGE_HISTORY

# Проверить наличие права
if Permissions.SEND_MESSAGES in permissions:
    print("Может отправлять сообщения")
```

### Все права

```python
# Основные
Permissions.CREATE_INSTANT_INVITE
Permissions.KICK_MEMBERS
Permissions.BAN_MEMBERS
Permissions.ADMINISTRATOR
Permissions.MANAGE_CHANNELS
Permissions.MANAGE_GUILD
Permissions.ADD_REACTIONS
Permissions.VIEW_AUDIT_LOG

# Сообщения
Permissions.SEND_MESSAGES
Permissions.SEND_TTS_MESSAGES
Permissions.MANAGE_MESSAGES
Permissions.EMBED_LINKS
Permissions.ATTACH_FILES
Permissions.READ_MESSAGE_HISTORY
Permissions.MENTION_EVERYONE

# Голос
Permissions.CONNECT
Permissions.SPEAK
Permissions.MUTE_MEMBERS
Permissions.DEAFEN_MEMBERS
Permissions.MOVE_MEMBERS
Permissions.USE_VAD

# Threads
Permissions.MANAGE_THREADS
Permissions.CREATE_PUBLIC_THREADS
Permissions.CREATE_PRIVATE_THREADS
Permissions.SEND_MESSAGES_IN_THREADS
```

## PermissionCalculator

### Вычисление прав

```python
from discordself.permissions import PermissionCalculator

calc = PermissionCalculator()

# Вычислить права для роли
role_permissions = calc.calculate_role_permissions(
    base_permissions=0,
    role_permissions=[Permissions.SEND_MESSAGES, Permissions.READ_MESSAGE_HISTORY]
)

# Вычислить права участника
member_permissions = calc.calculate_member_permissions(
    guild_permissions=Permissions.ADMINISTRATOR,
    roles=[role1, role2],
    channel_overwrites={}
)
```

### Проверка прав

```python
from discordself.permissions import has_permission, has_any_permission, has_all_permissions

# Проверить одно право
if has_permission(permissions, Permissions.SEND_MESSAGES):
    print("Может отправлять сообщения")

# Проверить любое из прав
if has_any_permission(permissions, Permissions.KICK_MEMBERS, Permissions.BAN_MEMBERS):
    print("Может кикать или банить")

# Проверить все права
if has_all_permissions(permissions, Permissions.SEND_MESSAGES, Permissions.READ_MESSAGE_HISTORY):
    print("Может отправлять и читать сообщения")
```

## Checks для команд

### has_permissions

```python
from discordself.checks import has_permissions
from discordself.permissions import Permissions

@bot.command(name="ban")
@has_permissions(Permissions.BAN_MEMBERS)
async def ban_command(ctx, user: UserConverter):
    await ctx.send(f"Banned {user.mention}")
```

### Несколько прав

```python
@bot.command(name="moderate")
@has_permissions(Permissions.KICK_MEMBERS | Permissions.BAN_MEMBERS)
async def moderate_command(ctx):
    await ctx.send("Moderation command")
```

### bot_has_permissions

```python
from discordself.checks import bot_has_permissions

@bot.command(name="delete")
@bot_has_permissions(Permissions.MANAGE_MESSAGES)
async def delete_command(ctx, count: int):
    # Бот должен иметь право MANAGE_MESSAGES
    await ctx.send(f"Would delete {count} messages")
```

## Примеры

### Проверка прав участника

```python
async def check_member_permissions(member, channel):
    """Проверить права участника в канале"""
    permissions = channel.permissions_for(member)
    
    if Permissions.ADMINISTRATOR in permissions:
        return "Администратор"
    elif Permissions.MANAGE_MESSAGES in permissions:
        return "Модератор"
    elif Permissions.SEND_MESSAGES in permissions:
        return "Обычный участник"
    else:
        return "Нет прав"
```

### Создание роли с правами

```python
from discordself.permissions import Permissions

# Создать роль модератора
moderator_permissions = (
    Permissions.MANAGE_MESSAGES |
    Permissions.KICK_MEMBERS |
    Permissions.BAN_MEMBERS |
    Permissions.MANAGE_CHANNELS
)

role = await client.create_role(
    guild_id=guild_id,
    name="Moderator",
    permissions=moderator_permissions
)
```

### Проверка прав перед действием

```python
@bot.command(name="kick")
async def kick_command(ctx, user: UserConverter):
    # Проверить права автора
    author_permissions = ctx.channel.permissions_for(ctx.author)
    
    if not (Permissions.KICK_MEMBERS in author_permissions or 
            Permissions.ADMINISTRATOR in author_permissions):
        await ctx.send("❌ У вас нет прав для кика!")
        return
    
    # Проверить права бота
    bot_member = ctx.guild.get_member(ctx.bot.client.user.id)
    bot_permissions = ctx.channel.permissions_for(bot_member)
    
    if not Permissions.KICK_MEMBERS in bot_permissions:
        await ctx.send("❌ У бота нет прав для кика!")
        return
    
    # Выполнить кик
    await ctx.send(f"✅ {user.mention} был исключен!")
```

## Permission Overwrites

### Создание overwrite

```python
# Разрешить роли отправлять сообщения
overwrite = {
    "id": role_id,
    "type": 0,  # ROLE
    "allow": Permissions.SEND_MESSAGES,
    "deny": 0
}

# Запретить пользователю отправлять сообщения
overwrite = {
    "id": user_id,
    "type": 1,  # MEMBER
    "allow": 0,
    "deny": Permissions.SEND_MESSAGES
}

# Применить к каналу
await client.modify_channel(
    channel_id=channel_id,
    permission_overwrites=[overwrite]
)
```

## Best Practices

1. **Всегда проверяйте права** перед выполнением действий
2. **Проверяйте права бота** тоже
3. **Используйте checks** для автоматической проверки
4. **Обрабатывайте ошибки** MissingPermissions
5. **Используйте PermissionCalculator** для сложных вычислений

