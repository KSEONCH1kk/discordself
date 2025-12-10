# DiscordSelf - Новые возможности

## ✅ Реализованные функции

### 1. Commands Framework ⭐⭐⭐⭐⭐
Полнофункциональная система команд с:
- Автоматическим парсингом аргументов
- Конвертацией типов (int, float, bool, User, Member, Channel)
- Поддержкой групп команд (subcommands)
- Context для доступа к сообщению, каналу, гильдии

**Пример:**
```python
from discordself.commands import Bot

bot = Bot(client, command_prefix="!")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command(name="add")
async def add(ctx, a: int, b: int):
    await ctx.send(f"{a} + {b} = {a + b}")
```

### 2. Cogs система ⭐⭐⭐⭐⭐
Модульная организация команд:
- Загрузка/выгрузка Cogs
- Автоматическая регистрация команд и listeners
- Методы жизненного цикла (cog_load, cog_unload)

**Пример:**
```python
from discordself.cogs import Cog, command, listener

class AdminCog(Cog):
    @command(name="shutdown")
    async def shutdown(self, ctx):
        await ctx.send("Выключаюсь...")
    
    @listener("ready")
    async def on_ready(self):
        print("AdminCog загружен!")

bot.cog_manager.add_cog(AdminCog(bot))
```

### 3. Расширенные исключения ⭐⭐⭐⭐⭐
Полный набор исключений:
- HTTP: `Forbidden`, `NotFound`, `BadRequest`, `Unauthorized`
- Commands: `CommandError`, `CommandNotFound`, `MissingRequiredArgument`, `BadArgument`, `CheckFailure`
- Permissions: `MissingPermissions`, `BotMissingPermissions`
- Channels: `NoPrivateMessage`, `PrivateMessageOnly`

### 4. Listeners система ⭐⭐⭐⭐⭐
Декоратор `@client.listen()` с поддержкой приоритетов:
```python
@client.listen("ready")
async def on_ready():
    print("Бот готов!")

@client.listen("message", priority=1)
async def on_message_high_priority(message):
    # Выполнится первым
    pass
```

### 5. Event dispatch с приоритетами ⭐⭐⭐⭐⭐
Обработчики событий с приоритетами (больше = выше приоритет)

### 6. Permissions Calculator ⭐⭐⭐⭐⭐
Утилита для работы с permissions:
- Проверка наличия permissions
- Добавление/удаление permissions
- Вычисление overwrites
- Работа с ролями

**Пример:**
```python
from discordself.permissions import Permissions, has_permission

perms = Permissions.SEND_MESSAGES | Permissions.VIEW_CHANNEL
if has_permission(perms, Permissions.SEND_MESSAGES):
    print("Может отправлять сообщения")
```

### 7. Checks система ⭐⭐⭐⭐
Проверки для команд:
- `has_permissions`, `bot_has_permissions`
- `has_role`, `has_any_role`
- `guild_only`, `dm_only`
- `is_owner`, `is_nsfw`
- `cooldown`

**Пример:**
```python
from discordself.checks import guild_only, has_permissions

@bot.command(name="kick", checks=[guild_only()])
async def kick(ctx, user: str):
    await ctx.send(f"Kicking {user}")
```

### 8. Улучшенная типизация ⭐⭐⭐⭐
Использование type hints:
- `Dict[str, Any]`, `List[Type]`, `Optional[Type]`
- `TYPE_CHECKING` для избежания circular imports
- Полная типизация методов

### 9. Unit тесты ⭐⭐⭐
Базовые тесты для:
- Permissions calculator
- Commands system
- Context

**Запуск:**
```bash
python -m pytest tests/
# или
python -m unittest discover tests
```

### 10. Voice Support ⭐⭐
Базовая поддержка Voice:
- `VoiceClient` для подключения к голосовым каналам
- `VoiceState` для отслеживания состояния
- Подключение/отключение от каналов

**Пример:**
```python
from discordself.voice import VoiceClient

async with VoiceClient(client, channel) as voice:
    print("Подключен к голосовому каналу")
    # Логика работы с голосом
```

## 📊 Статистика

- **Commands Framework**: ✅ Полностью реализован
- **Cogs система**: ✅ Полностью реализована
- **Расширенные исключения**: ✅ 20+ типов исключений
- **Listeners**: ✅ С приоритетами
- **Permissions Calculator**: ✅ Полный функционал
- **Checks**: ✅ Все основные проверки
- **Типизация**: ✅ Улучшена
- **Unit тесты**: ✅ Базовые тесты
- **Voice Support**: ⚠️ Базовая поддержка (без аудио стриминга)

## 🚀 Использование

См. примеры в:
- `example_commands.py` - примеры команд
- `example_permissions.py` - примеры работы с permissions
- `example_voice.py` - примеры работы с голосом

## 📝 Примечания

- Voice Support реализован на базовом уровне (подключение/отключение)
- Для полноценного аудио стриминга требуется дополнительная реализация
- Все основные функции из списка требований реализованы

