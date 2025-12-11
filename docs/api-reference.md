# API Reference

Полная документация API DiscordSelf.

## Client

Основной класс для взаимодействия с Discord.

### Инициализация

```python
from discordself import Client, Intents

client = Client(
    token: str,
    shard_count: int = 1,
    intents: int = 0,
    enable_cache: bool = True
)
```

**Параметры:**
- `token` (str): Токен Discord аккаунта
- `shard_count` (int): Количество шардов (по умолчанию 1)
- `intents` (int): Intents для Gateway (по умолчанию 0)
- `enable_cache` (bool): Включить кэширование (по умолчанию True)

### Методы

#### Управление соединением

##### `async start()`
Запустить клиент и подключиться к Discord.

```python
await client.start()
```

##### `async close()`
Закрыть клиент и отключиться от Discord.

```python
await client.close()
```

##### `async login()`
Войти в Discord (получить информацию о пользователе).

```python
await client.login()
```

##### `async connect()`
Подключиться к Gateway.

```python
await client.connect()
```

#### Сообщения

##### `async send_message(channel_id, content=None, embeds=None, components=None, files=None, tts=False, allowed_mentions=None, flags=0, thread_id=None)`
Отправить сообщение в канал.

**Параметры:**
- `channel_id` (int): ID канала
- `content` (str, optional): Текст сообщения
- `embeds` (List[Embed], optional): Список embeds
- `components` (List[ActionRow], optional): Компоненты (кнопки, меню)
- `files` (List[Dict], optional): Файлы для отправки
- `tts` (bool): Text-to-speech
- `allowed_mentions` (Dict, optional): Разрешенные упоминания
- `flags` (int): Флаги сообщения
- `thread_id` (int, optional): ID нити

**Возвращает:** `Dict` - данные отправленного сообщения

**Пример:**
```python
await client.send_message(
    channel_id=123456789,
    content="Hello, World!",
    embeds=[embed]
)
```

##### `async edit_message(channel_id, message_id, content=None, embeds=None, components=None, files=None, allowed_mentions=None, flags=None)`
Редактировать сообщение.

##### `async delete_message(channel_id, message_id)`
Удалить сообщение.

##### `async fetch_message(channel_id, message_id)`
Получить сообщение по ID.

##### `async fetch_messages(channel_id, limit=50, before=None, after=None, around=None)`
Получить сообщения канала.

##### `async fetch_all_messages(channel_id, limit=None, check=None)`
Получить все сообщения канала с пагинацией.

##### `async search_messages(guild_id, content=None, has=None, max_id=None, min_id=None, author_id=None, author_type=None, mentions=None, mentions_everyone=None, has_embed=None, has_file=None, has_link=None, has_video=None, has_image=None, has_sound=None, channel_id=None, limit=25, offset=0, sort_by=None, sort_order=None)`
Поиск сообщений в гильдии.

#### Каналы

##### `async fetch_channel(channel_id)`
Получить канал по ID.

##### `async create_channel(guild_id, name, type=0, topic=None, bitrate=None, user_limit=None, rate_limit_per_user=None, position=None, permission_overwrites=None, parent_id=None, nsfw=None, reason=None)`
Создать канал.

##### `async modify_channel(channel_id, name=None, type=None, position=None, topic=None, nsfw=None, rate_limit_per_user=None, bitrate=None, user_limit=None, permission_overwrites=None, parent_id=None, reason=None)`
Изменить канал.

##### `async delete_channel(channel_id, reason=None)`
Удалить канал.

#### Гильдии

##### `async fetch_guild(guild_id, with_counts=False)`
Получить гильдию по ID.

##### `async modify_guild(guild_id, name=None, icon=None, verification_level=None, default_message_notifications=None, explicit_content_filter=None, afk_channel_id=None, afk_timeout=None, owner_id=None, splash=None, banner=None, system_channel_id=None, rules_channel_id=None, public_updates_channel_id=None, preferred_locale=None, features=None, description=None, reason=None)`
Изменить гильдию.

#### Участники и роли

##### `async ban_user(guild_id, user_id, delete_message_days=0, reason=None)`
Забанить пользователя.

##### `async unban_user(guild_id, user_id, reason=None)`
Разбанить пользователя.

##### `async kick_member(guild_id, user_id, reason=None)`
Исключить участника.

##### `async add_role(guild_id, user_id, role_id, reason=None)`
Добавить роль участнику.

##### `async remove_role(guild_id, user_id, role_id, reason=None)`
Удалить роль у участника.

##### `async modify_member(guild_id, user_id, nick=None, roles=None, mute=None, deaf=None, channel_id=None, reason=None)`
Изменить участника.

##### `async create_role(guild_id, name, permissions=None, color=None, hoist=None, mentionable=None, icon=None, unicode_emoji=None, reason=None)`
Создать роль.

##### `async modify_role(guild_id, role_id, name=None, permissions=None, color=None, hoist=None, mentionable=None, icon=None, unicode_emoji=None, reason=None)`
Изменить роль.

##### `async delete_role(guild_id, role_id, reason=None)`
Удалить роль.

#### Реакции

##### `async add_reaction(channel_id, message_id, emoji)`
Добавить реакцию.

##### `async remove_reaction(channel_id, message_id, emoji, user_id=None)`
Удалить реакцию.

##### `async get_reactions(channel_id, message_id, emoji, after=None, limit=25)`
Получить пользователей, поставивших реакцию.

##### `async remove_all_reactions(channel_id, message_id)`
Удалить все реакции.

##### `async remove_all_reactions_for_emoji(channel_id, message_id, emoji)`
Удалить все реакции для эмодзи.

#### Webhooks

##### `async create_webhook(channel_id, name, avatar=None, reason=None)`
Создать webhook.

##### `async get_channel_webhooks(channel_id)`
Получить webhooks канала.

##### `async get_guild_webhooks(guild_id)`
Получить webhooks гильдии.

##### `get_webhook(webhook_id, webhook_token)`
Получить объект Webhook.

#### Threads

##### `async start_thread_with_message(channel_id, message_id, name, auto_archive_duration=None)`
Создать нить из сообщения.

##### `async start_thread_without_message(channel_id, name, auto_archive_duration=None, type=None, invitable=None)`
Создать нить без сообщения.

##### `async join_thread(channel_id)`
Присоединиться к нити.

##### `async leave_thread(channel_id)`
Покинуть нить.

##### `async list_active_threads(guild_id)`
Получить активные нити гильдии.

#### AutoMod

##### `async get_automod_rules(guild_id)`
Получить все правила AutoMod.

##### `async get_automod_rule(guild_id, rule_id)`
Получить правило AutoMod по ID.

##### `async create_automod_rule(guild_id, name, event_type, trigger_type, trigger_metadata=None, actions=None, enabled=True, exempt_roles=None, exempt_channels=None)`
Создать правило AutoMod.

##### `async modify_automod_rule(guild_id, rule_id, name=None, event_type=None, trigger_metadata=None, actions=None, enabled=None, exempt_roles=None, exempt_channels=None)`
Изменить правило AutoMod.

##### `async delete_automod_rule(guild_id, rule_id)`
Удалить правило AutoMod.

#### Scheduled Events

##### `async list_scheduled_events(guild_id, with_user_count=False)`
Получить все Scheduled Events гильдии.

##### `async get_scheduled_event(guild_id, event_id, with_user_count=False)`
Получить Scheduled Event по ID.

##### `async create_scheduled_event(guild_id, name, scheduled_start_time, entity_type, channel_id=None, entity_metadata=None, scheduled_end_time=None, description=None, privacy_level=2, image=None)`
Создать Scheduled Event.

##### `async modify_scheduled_event(guild_id, event_id, name=None, description=None, scheduled_start_time=None, scheduled_end_time=None, entity_type=None, channel_id=None, entity_metadata=None, privacy_level=None, status=None, image=None)`
Изменить Scheduled Event.

##### `async delete_scheduled_event(guild_id, event_id)`
Удалить Scheduled Event.

#### Другое

##### `async change_presence(status=None, activities=None, afk=False)`
Изменить статус и активность.

##### `async wait_for(event, check=None, timeout=None)`
Ожидать событие.

##### `get_channel(channel_id)`
Получить канал из кэша.

##### `get_guild(guild_id)`
Получить гильдию из кэша.

##### `get_user(user_id)`
Получить пользователя из кэша.

### События

#### `ready`
Вызывается когда клиент готов к работе.

```python
@client.event("ready")
async def on_ready():
    print(f"Logged in as {client.user}")
```

#### `message` / `message_create`
Вызывается при получении нового сообщения.

```python
@client.event("message")
async def on_message(message):
    print(f"Message: {message.content}")
```

#### `message_update`
Вызывается при обновлении сообщения.

#### `message_delete`
Вызывается при удалении сообщения.

#### `guild_join`
Вызывается при присоединении к гильдии.

#### `guild_update`
Вызывается при обновлении гильдии.

#### `guild_remove`
Вызывается при покидании гильдии.

#### `channel_create`
Вызывается при создании канала.

#### `channel_update`
Вызывается при обновлении канала.

#### `channel_delete`
Вызывается при удалении канала.

#### `interaction_create`
Вызывается при создании interaction.

#### `modal_submit`
Вызывается при отправке модального окна.

#### `automod_action_execution`
Вызывается при выполнении действия AutoMod.

## Models

### User

Модель пользователя Discord.

**Атрибуты:**
- `id` (int): ID пользователя
- `username` (str): Имя пользователя
- `discriminator` (str): Дискриминатор
- `global_name` (str, optional): Глобальное имя
- `avatar` (str, optional): Аватар
- `bot` (bool): Является ли ботом
- `system` (bool): Системный пользователь
- `verified` (bool): Верифицирован
- `email` (str, optional): Email

**Методы:**
- `mention` (property): Упоминание пользователя (`<@id>`)

### Guild

Модель гильдии (сервера).

**Атрибуты:**
- `id` (int): ID гильдии
- `name` (str): Название
- `icon` (str, optional): Иконка
- `owner_id` (int): ID владельца
- `member_count` (int): Количество участников
- `channels` (Dict[int, Channel]): Каналы
- `members` (Dict[int, Member]): Участники
- `roles` (Dict[int, Role]): Роли

### Channel

Модель канала.

**Атрибуты:**
- `id` (int): ID канала
- `name` (str): Название
- `type` (ChannelType): Тип канала
- `guild_id` (int, optional): ID гильдии
- `position` (int): Позиция
- `topic` (str, optional): Тема

### Message

Модель сообщения.

**Атрибуты:**
- `id` (int): ID сообщения
- `channel_id` (int): ID канала
- `author` (User): Автор
- `content` (str): Содержимое
- `timestamp` (str): Время создания
- `embeds` (List[Dict]): Embeds
- `attachments` (List[Attachment]): Вложения
- `reactions` (List[Dict]): Реакции

**Методы:**
- `async send(content=None, embeds=None, ...)`: Ответить на сообщение
- `async edit(content=None, embeds=None, ...)`: Редактировать сообщение
- `async delete()`: Удалить сообщение
- `async add_reaction(emoji)`: Добавить реакцию
- `async remove_reaction(emoji)`: Удалить реакцию

### Attachment

Модель вложения.

**Атрибуты:**
- `id` (int): ID вложения
- `filename` (str): Имя файла
- `size` (int): Размер в байтах
- `url` (str): URL файла
- `content_type` (str, optional): MIME тип
- `width` (int, optional): Ширина (для изображений)
- `height` (int, optional): Высота (для изображений)

**Методы:**
- `is_image` (property): Является ли изображением
- `is_video` (property): Является ли видео
- `is_audio` (property): Является ли аудио

### Invite

Модель приглашения.

**Атрибуты:**
- `code` (str): Код приглашения
- `guild_id` (int, optional): ID гильдии
- `channel_id` (int, optional): ID канала
- `inviter` (User, optional): Создатель приглашения
- `uses` (int): Количество использований
- `max_uses` (int): Максимальное количество использований
- `max_age` (int): Время жизни в секундах
- `temporary` (bool): Временное приглашение

**Методы:**
- `url` (property): URL приглашения (`https://discord.gg/{code}`)

### Interaction

Модель interaction (включая Modals).

**Атрибуты:**
- `id` (int): ID interaction
- `type` (InteractionType): Тип interaction
- `token` (str): Токен interaction
- `guild_id` (int, optional): ID гильдии
- `channel_id` (int, optional): ID канала
- `user` (User, optional): Пользователь
- `data` (Dict): Данные interaction
- `custom_id` (str): Custom ID (для модальных окон)
- `components` (List[Dict]): Компоненты (для модальных окон)

**Методы:**
- `get_modal_value(custom_id)`: Получить значение поля модального окна
- `async respond(content=None, embeds=None, ...)`: Ответить на interaction
- `async respond_modal(custom_id, title, components)`: Ответить модальным окном

### AutoModRule

Модель правила AutoMod.

**Атрибуты:**
- `id` (int): ID правила
- `guild_id` (int): ID гильдии
- `name` (str): Название правила
- `event_type` (int): Тип события
- `trigger_type` (int): Тип триггера
- `trigger_metadata` (Dict): Метаданные триггера
- `actions` (List[Dict]): Действия
- `enabled` (bool): Включено ли правило
- `exempt_roles` (List[int]): Исключенные роли
- `exempt_channels` (List[int]): Исключенные каналы

## Enums

### Status

Статус пользователя.

```python
Status.ONLINE
Status.IDLE
Status.DND
Status.INVISIBLE
Status.OFFLINE
```

### ChannelType

Тип канала.

```python
ChannelType.GUILD_TEXT
ChannelType.DM
ChannelType.GUILD_VOICE
ChannelType.GUILD_CATEGORY
ChannelType.GUILD_NEWS
ChannelType.GUILD_STAGE_VOICE
ChannelType.GUILD_FORUM
```

### InteractionType

Тип interaction.

```python
InteractionType.PING
InteractionType.APPLICATION_COMMAND
InteractionType.MESSAGE_COMPONENT
InteractionType.MODAL_SUBMIT
```

### AutoModEventType

Тип события AutoMod.

```python
AutoModEventType.MESSAGE_SEND
```

### AutoModTriggerType

Тип триггера AutoMod.

```python
AutoModTriggerType.KEYWORD
AutoModTriggerType.SPAM
AutoModTriggerType.KEYWORD_PRESET
AutoModTriggerType.MENTION_SPAM
```

### AutoModActionType

Тип действия AutoMod.

```python
AutoModActionType.BLOCK_MESSAGE
AutoModActionType.SEND_ALERT_MESSAGE
AutoModActionType.TIMEOUT
```

## Exceptions

### DiscordException

Базовое исключение для всех ошибок DiscordSelf.

### HTTPException

Ошибка HTTP запроса.

**Атрибуты:**
- `status` (int): HTTP статус код
- `code` (int): Код ошибки Discord
- `message` (str): Сообщение об ошибке

### RateLimitException

Превышен rate limit.

### WebSocketException

Ошибка WebSocket соединения.

### LoginFailure

Ошибка входа в Discord.

### CommandError

Базовое исключение для ошибок команд.

### CommandNotFound

Команда не найдена.

### MissingRequiredArgument

Отсутствует обязательный аргумент.

### BadArgument

Неверный аргумент.

### CheckFailure

Проверка не пройдена.

### MissingPermissions

Отсутствуют необходимые права.

### CommandOnCooldown

Команда на cooldown.

**Атрибуты:**
- `retry_after` (float): Время до следующего использования в секундах

