# DiscordSelf Wiki

Добро пожаловать в вики DiscordSelf! Здесь собрана вся информация о библиотеке.

## Содержание

### Основы
- [Что такое DiscordSelf?](#что-такое-discordself)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)

### Основные концепции
- [Client](#client)
- [События](#события)
- [Модели данных](#модели-данных)
- [Intents](#intents)

### Функциональность
- [Система команд](#система-команд)
- [Голосовые функции](#голосовые-функции)
- [Embeds и компоненты](#embeds-и-компоненты)
- [Webhooks](#webhooks)
- [Threads](#threads)
- [AutoMod](#automod)
- [Modals](#modals)

### Продвинутые темы
- [Cogs](#cogs)
- [Permissions](#permissions)
- [Шардирование](#шардирование)
- [Кэширование](#кэширование)
- [Rate Limiting](#rate-limiting)

## Что такое DiscordSelf?

DiscordSelf - это библиотека для создания Discord selfbot на Python. Она позволяет автоматизировать действия вашего личного Discord аккаунта через User Token.

### Отличия от discord.py

| Особенность | DiscordSelf | discord.py |
|-------------|------------|------------|
| Тип токена | User Token | Bot Token |
| Целевая аудитория | Пользователи | Боты |
| ToS Discord | ❌ Нарушает | ✅ Соответствует |
| Slash Commands | ❌ | ✅ |

## Установка

```bash
pip install discordself
```

Или из исходников:

```bash
git clone https://github.com/yourusername/discordself.git
cd discordself
pip install -r requirements.txt
```

## Быстрый старт

```python
import asyncio
from discordself import Client, Intents

client = Client(
    token="YOUR_TOKEN",
    intents=Intents.GUILD_MESSAGES | Intents.MESSAGE_CONTENT
)

@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")

@client.event("message")
async def on_message(message):
    if message.content == "!ping":
        await message.channel.send("🏓 Pong!")

async def main():
    async with client:
        await asyncio.sleep(3600)

asyncio.run(main())
```

## Client

`Client` - основной класс для взаимодействия с Discord.

### Инициализация

```python
client = Client(
    token="YOUR_TOKEN",
    shard_count=1,
    intents=Intents.DEFAULT,
    enable_cache=True
)
```

### Основные методы

- `start()` - Запустить клиент
- `close()` - Закрыть клиент
- `send_message()` - Отправить сообщение
- `fetch_channel()` - Получить канал
- `wait_for()` - Ожидать событие

## События

События обрабатываются через декораторы:

```python
@client.event("ready")
async def on_ready():
    pass

@client.listen("message", priority=1)
async def on_message(message):
    pass
```

### Доступные события

- `ready` - Клиент готов
- `message` / `message_create` - Новое сообщение
- `message_update` - Сообщение обновлено
- `message_delete` - Сообщение удалено
- `guild_join` - Присоединение к гильдии
- `channel_create` - Создание канала
- `interaction_create` - Создание interaction
- `modal_submit` - Отправка модального окна
- `automod_action_execution` - Действие AutoMod

## Модели данных

### User

```python
user.id          # ID пользователя
user.username    # Имя пользователя
user.avatar      # Аватар
user.mention     # Упоминание (<@id>)
```

### Guild

```python
guild.id            # ID гильдии
guild.name          # Название
guild.member_count  # Количество участников
guild.channels      # Каналы
guild.members       # Участники
```

### Message

```python
message.id          # ID сообщения
message.content     # Содержимое
message.author      # Автор
message.channel     # Канал
message.embeds      # Embeds
message.attachments # Вложения
```

## Intents

Intents определяют, какие события вы получаете:

```python
Intents.GUILD_MESSAGES      # Сообщения в гильдиях
Intents.MESSAGE_CONTENT     # Содержимое сообщений
Intents.GUILD_MEMBERS       # Участники гильдий
Intents.GUILD_VOICE_STATES  # Голосовые состояния
Intents.DIRECT_MESSAGES     # Прямые сообщения
```

## Система команд

### Создание команды

```python
from discordself.commands import Bot

bot = Bot(client, command_prefix="!")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong!")
```

### Парсинг аргументов

```python
@bot.command(name="add")
async def add(ctx, a: int, b: int):
    await ctx.send(f"{a} + {b} = {a + b}")
```

### Checks и Cooldowns

```python
from discordself.checks import has_permissions, cooldown
from discordself.permissions import Permissions

@bot.command(name="ban")
@has_permissions(Permissions.BAN_MEMBERS)
@cooldown(rate=1, per=5.0)
async def ban(ctx, user: UserConverter):
    await ctx.send(f"Banned {user.mention}")
```

## Голосовые функции

### Подключение

```python
from discordself.voice import VoiceClient

channel = await client.fetch_channel(channel_id)
voice_client = await channel.connect()
```

### Воспроизведение

```python
from discordself.ffmpeg import FFmpegOpusAudio

source = FFmpegOpusAudio("music.mp3")
voice_client.play(source)
```

## Embeds и компоненты

### Embed

```python
from discordself import Embed

embed = Embed(
    title="Заголовок",
    description="Описание",
    color=0x00ff00
)
embed.add_field(name="Поле", value="Значение")
```

### Кнопки

```python
from discordself import Button, ActionRow

button = Button(Button.STYLE_PRIMARY, "Нажми", "btn1")
row = ActionRow()
row.add_button(button)
```

## Webhooks

```python
from discordself import Webhook

webhook = client.get_webhook(webhook_id, webhook_token)
await webhook.send(content="Hello from webhook!")
```

## Threads

```python
# Создать нить
thread = await client.start_thread_with_message(
    channel_id=channel_id,
    message_id=message_id,
    name="Обсуждение"
)

# Присоединиться
await client.join_thread(channel_id=thread_id)
```

## AutoMod

```python
# Создать правило
rule = await client.create_automod_rule(
    guild_id=guild_id,
    name="Блокировка мата",
    event_type=AutoModEventType.MESSAGE_SEND,
    trigger_type=AutoModTriggerType.KEYWORD,
    trigger_metadata={"keyword_filter": ["мат"]},
    actions=[{"type": AutoModActionType.BLOCK_MESSAGE}]
)
```

## Modals

```python
# Открыть модальное окно
await interaction.respond_modal(
    custom_id="form",
    title="Форма",
    components=[...]
)

# Обработать отправку
@client.event("modal_submit")
async def on_modal_submit(interaction):
    value = interaction.get_modal_value("field_id")
```

## Cogs

```python
from discordself.cogs import Cog, command

class MyCog(Cog):
    @command(name="hello")
    async def hello(self, ctx):
        await ctx.send("Hello from Cog!")

bot.cog_manager.add_cog(MyCog(bot))
```

## Permissions

```python
from discordself.permissions import Permissions, has_permission

permissions = Permissions.SEND_MESSAGES | Permissions.READ_MESSAGE_HISTORY

if has_permission(permissions, Permissions.SEND_MESSAGES):
    print("Может отправлять сообщения")
```

## Шардирование

Для больших ботов используйте шардирование:

```python
client = Client(token="YOUR_TOKEN", shard_count=4)
```

## Кэширование

Кэширование включено по умолчанию:

```python
client = Client(token="YOUR_TOKEN", enable_cache=True)

# Получить из кэша
channel = client.get_channel(channel_id)
```

## Rate Limiting

DiscordSelf автоматически обрабатывает rate limits. При необходимости можно добавить задержки:

```python
import asyncio

async def safe_send(channel_id, content):
    await client.send_message(channel_id=channel_id, content=content)
    await asyncio.sleep(1)  # Задержка между сообщениями
```

## Best Practices

1. **Безопасность токена** - Никогда не публикуйте токен
2. **Обработка ошибок** - Всегда обрабатывайте исключения
3. **Rate limiting** - Соблюдайте ограничения Discord
4. **Логирование** - Логируйте важные события
5. **Кэширование** - Используйте кэш для производительности

## Troubleshooting

### Команды не работают

1. Проверьте intents: `Intents.GUILD_MESSAGES | Intents.MESSAGE_CONTENT`
2. Убедитесь, что префикс правильный
3. Проверьте регистр команды

### Голос не работает

1. Убедитесь, что FFmpeg установлен
2. Проверьте наличие `opus.dll` (Windows)
3. Проверьте подключение к каналу

### Rate limit ошибки

1. Уменьшите частоту запросов
2. Используйте кэширование
3. Добавьте задержки

## Дополнительные ресурсы

- [API Reference](api-reference.md)
- [Примеры](examples/)
- [FAQ](faq.md)
- [GitHub](https://github.com/yourusername/discordself)

