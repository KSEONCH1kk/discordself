# Базовые примеры

## Простой бот

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

## Бот с командами

```python
import asyncio
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

@bot.command(name="hello")
async def hello(ctx):
    await ctx.send(f"Привет, {ctx.author.mention}!")

@bot.command(name="add")
async def add(ctx, a: int, b: int):
    await ctx.send(f"{a} + {b} = {a + b}")

async def main():
    async with client:
        await asyncio.sleep(3600)

asyncio.run(main())
```

## Отправка сообщений

### Простое сообщение

```python
await client.send_message(channel_id=123456789, content="Hello, World!")
```

### Сообщение с Embed

```python
from discordself import Embed

embed = Embed(
    title="Заголовок",
    description="Описание",
    color=0x00ff00
)
embed.add_field(name="Поле 1", value="Значение 1", inline=False)
embed.add_field(name="Поле 2", value="Значение 2", inline=True)

await client.send_message(
    channel_id=123456789,
    embeds=[embed]
)
```

### Сообщение с файлом

```python
with open("image.png", "rb") as f:
    await client.send_message(
        channel_id=123456789,
        content="Вот изображение:",
        files=[{"file": f, "filename": "image.png"}]
    )
```

### Сообщение с кнопками

```python
from discordself import Button, ActionRow

button1 = Button(
    Button.STYLE_PRIMARY,
    label="Кнопка 1",
    custom_id="btn1"
)
button2 = Button(
    Button.STYLE_SECONDARY,
    label="Кнопка 2",
    custom_id="btn2"
)

row = ActionRow()
row.add_button(button1)
row.add_button(button2)

await client.send_message(
    channel_id=123456789,
    content="Выберите действие:",
    components=[row]
)
```

## Работа с каналами

### Получить канал

```python
channel = await client.fetch_channel(channel_id=123456789)
print(f"Канал: {channel.name}")
```

### Создать канал

```python
channel = await client.create_channel(
    guild_id=123456789,
    name="новый-канал",
    type=0  # TEXT_CHANNEL
)
```

### Получить все сообщения

```python
messages = await client.fetch_all_messages(channel_id=123456789, limit=100)
for message in messages:
    print(f"{message.author}: {message.content}")
```

## Работа с гильдиями

### Получить гильдию

```python
guild = await client.fetch_guild(guild_id=123456789)
print(f"Гильдия: {guild.name}")
print(f"Участников: {guild.member_count}")
```

### Получить участников

```python
guild = await client.fetch_guild(guild_id=123456789)
for member_id, member in guild.members.items():
    print(f"{member.user.username}")
```

## Реакции

### Добавить реакцию

```python
await client.add_reaction(
    channel_id=123456789,
    message_id=987654321,
    emoji="👍"
)
```

### Получить реакции

```python
reactions = await client.get_reactions(
    channel_id=123456789,
    message_id=987654321,
    emoji="👍"
)
for user in reactions:
    print(f"{user.username} поставил 👍")
```

## Webhooks

### Создать webhook

```python
webhook_data = await client.create_webhook(
    channel_id=123456789,
    name="My Webhook"
)

webhook = client.get_webhook(
    webhook_data["id"],
    webhook_data["token"]
)
```

### Отправить через webhook

```python
from discordself import Embed

embed = Embed(title="Webhook", color=0xff0000)
await webhook.send(
    content="Привет из webhook!",
    embeds=[embed],
    username="Custom Name"
)
```

## Изменение статуса

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

## Ожидание события

```python
# Ожидать сообщение от конкретного пользователя
message = await client.wait_for(
    "message",
    check=lambda m: m.author.id == 123456789,
    timeout=60
)
print(f"Получено: {message.content}")
```

