# DiscordSelf

Полнофункциональная библиотека для создания Discord selfbot на Python.

## Возможности

- ✅ **REST API** - Полная поддержка Discord REST API
- ✅ **WebSocket** - Поддержка Gateway для получения событий в реальном времени
- ✅ **Шардирование** - Поддержка множественных шардов для больших ботов
- ✅ **Rate-limit менеджер** - Автоматическое управление rate limits
- ✅ **Кэширование** - Эффективная система кэширования объектов
- ✅ **Модели данных** - Полные модели для всех Discord объектов
- ✅ **Асинхронность** - Полностью асинхронный API на основе asyncio
- ✅ **Embeds** - Полная поддержка embed сообщений
- ✅ **Компоненты** - Кнопки, выпадающие меню, Action Rows
- ✅ **Файлы** - Отправка файлов в сообщениях
- ✅ **Webhooks** - Полная поддержка Discord Webhooks
- ✅ **Расширенное чтение** - Чтение всех сообщений с пагинацией и фильтрами
- ✅ **Поиск сообщений** - Поиск по гильдиям с различными фильтрами
- ✅ **Реакции** - Управление реакциями на сообщения
- ✅ **Управление гильдиями** - Создание/изменение каналов, ролей, участников
- ✅ **Нитки (Threads)** - Полная поддержка нитей Discord

## Установка

```bash
pip install -r requirements.txt
```

Или через pip:

```bash
pip install discordself
```

## Быстрый старт

```python
import asyncio
from discordself import Client

client = Client(token="YOUR_TOKEN")

@client.event("ready")
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event("message")
async def on_message(message):
    if message.content == "!ping":
        await message.channel.send("Pong!")

async def main():
    async with client:
        await asyncio.sleep(3600)  # Работать 1 час

asyncio.run(main())
```

## Примеры использования

### Отправка сообщения

```python
await client.send_message(channel_id=123456789, content="Hello, World!")
```

### Отправка сообщения с Embed

```python
from discordself import Embed

embed = Embed(
    title="Заголовок",
    description="Описание",
    color=0x00ff00
)
embed.add_field(name="Поле", value="Значение", inline=False)

await client.send_message(
    channel_id=123456789,
    embeds=[embed]
)
```

### Отправка сообщения с кнопками

```python
from discordself import Button, ActionRow

button = Button(
    Button.STYLE_PRIMARY,
    label="Нажми меня",
    custom_id="button_1"
)

row = ActionRow()
row.add_button(button)

await client.send_message(
    channel_id=123456789,
    content="Выберите действие:",
    components=[row]
)
```

### Отправка сообщения с файлами

```python
with open("image.png", "rb") as f:
    await client.send_message(
        channel_id=123456789,
        content="Вот изображение:",
        files=[{"file": f, "filename": "image.png"}]
    )
```

### Чтение всех сообщений канала

```python
# Получить все сообщения (с пагинацией)
messages = await client.fetch_all_messages(channel_id=123456789, limit=1000)

# С фильтром
def check(msg_data):
    return len(msg_data.get("content", "")) > 10

messages = await channel.fetch_all_messages(limit=500, check=check)
```

### Поиск сообщений

```python
results = await client.search_messages(
    guild_id=123456789,
    has="ключевое слово",
    author_id=987654321,
    limit=25
)
```

### Работа с Webhooks

```python
from discordself import Webhook

# Создать webhook
webhook_data = await client.create_webhook(channel_id=123456789, name="My Webhook")

# Использовать webhook
webhook = client.get_webhook(webhook_data["id"], webhook_data["token"])

embed = Embed(title="Webhook сообщение", color=0xff0000)
await webhook.send(
    content="Привет из webhook!",
    embeds=[embed],
    username="Custom Name"
)
```

### Получение гильдии

```python
guild = await client.fetch_guild(guild_id=123456789)
print(f"Guild: {guild.name}")
```

### Редактирование сообщения

```python
message = await client.send_message(channel_id=123456789, content="Original")
await client.edit_message(channel_id=123456789, message_id=message.id, content="Edited")
```

### Изменение статуса

```python
from discordself import Status

await client.change_presence(
    status=Status.ONLINE,
    activities=[{
        "name": "Python",
        "type": 0  # Playing
    }]
)
```

### Шардирование

```python
client = Client(token="YOUR_TOKEN", shard_count=2)
```

### Ожидание события

```python
message = await client.wait_for("message", check=lambda m: m.author.id == 123456789, timeout=60)
```

## Структура проекта

```
discordself/
├── __init__.py          # Основной модуль
├── client.py            # Главный клиент
├── http.py              # HTTP клиент для REST API
├── gateway.py           # WebSocket клиент для Gateway
├── shard.py             # Шардирование
├── ratelimit.py         # Rate-limit менеджер
├── cache.py             # Система кэширования
├── models.py            # Модели данных
├── enums.py             # Перечисления
└── exceptions.py        # Исключения
```

## API Документация

### Client

Основной класс клиента.

#### Параметры

- `token` (str): Токен Discord аккаунта
- `shard_count` (int): Количество шардов (по умолчанию 1)
- `intents` (int): Intents для Gateway (по умолчанию 0)
- `enable_cache` (bool): Включить кэширование (по умолчанию True)

#### Методы

#### Сообщения
- `send_message(channel_id, content, embeds, components, files, ...)` - Отправить сообщение
- `edit_message(channel_id, message_id, ...)` - Редактировать сообщение
- `delete_message(channel_id, message_id)` - Удалить сообщение
- `fetch_message(channel_id, message_id)` - Получить сообщение
- `fetch_messages(channel_id, limit, before, after, around)` - Получить сообщения
- `fetch_all_messages(channel_id, limit, check)` - Получить все сообщения с пагинацией
- `search_messages(guild_id, ...)` - Поиск сообщений

#### Каналы
- `fetch_channel(channel_id)` - Получить канал
- `create_channel(guild_id, name, type, ...)` - Создать канал
- `modify_channel(channel_id, ...)` - Изменить канал
- `delete_channel(channel_id)` - Удалить канал

#### Гильдии
- `fetch_guild(guild_id)` - Получить гильдию
- `modify_guild(guild_id, ...)` - Изменить гильдию

#### Участники и роли
- `ban_user(guild_id, user_id, ...)` - Забанить пользователя
- `unban_user(guild_id, user_id)` - Разбанить пользователя
- `kick_member(guild_id, user_id)` - Исключить участника
- `add_role(guild_id, user_id, role_id)` - Добавить роль
- `remove_role(guild_id, user_id, role_id)` - Удалить роль
- `modify_member(guild_id, user_id, ...)` - Изменить участника
- `create_role(guild_id, ...)` - Создать роль
- `modify_role(guild_id, role_id, ...)` - Изменить роль
- `delete_role(guild_id, role_id)` - Удалить роль

#### Реакции
- `get_reactions(channel_id, message_id, emoji, ...)` - Получить реакции
- `remove_all_reactions(channel_id, message_id)` - Удалить все реакции
- `remove_all_reactions_for_emoji(channel_id, message_id, emoji)` - Удалить реакции эмодзи

#### Webhooks
- `create_webhook(channel_id, name, ...)` - Создать webhook
- `get_channel_webhooks(channel_id)` - Получить webhooks канала
- `get_guild_webhooks(guild_id)` - Получить webhooks гильдии
- `get_webhook(webhook_id, webhook_token)` - Получить объект Webhook

#### Другое
- `start()` - Запустить клиент
- `close()` - Закрыть клиент
- `change_presence(status, activities, afk)` - Изменить статус
- `wait_for(event, check, timeout)` - Ожидать событие

### Модели

- `User` - Пользователь
- `Guild` - Гильдия (сервер)
- `Channel` - Канал
- `Message` - Сообщение
- `Member` - Участник гильдии
- `Role` - Роль
- `Emoji` - Эмодзи

## События

- `ready` - Клиент готов
- `message` / `message_create` - Новое сообщение
- `message_update` - Сообщение обновлено
- `message_delete` - Сообщение удалено
- `guild_join` - Присоединение к гильдии
- `guild_update` - Обновление гильдии
- `guild_remove` - Покидание гильдии
- `channel_create` - Создание канала
- `channel_update` - Обновление канала
- `channel_delete` - Удаление канала

## Лицензия

MIT License

## Важное замечание

Использование selfbot нарушает Terms of Service Discord. Используйте на свой риск.

