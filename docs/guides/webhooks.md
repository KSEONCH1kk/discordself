# Webhooks

Webhooks позволяют отправлять сообщения от имени бота без использования бота.

## Создание Webhook

### Создать webhook

```python
webhook_data = await client.create_webhook(
    channel_id=123456789,
    name="My Webhook",
    avatar=None  # URL аватара (опционально)
)

print(f"Webhook ID: {webhook_data['id']}")
print(f"Webhook Token: {webhook_data['token']}")
```

### Получить объект Webhook

```python
from discordself import Webhook

webhook = client.get_webhook(
    webhook_id=webhook_data["id"],
    webhook_token=webhook_data["token"]
)
```

## Отправка сообщений

### Простое сообщение

```python
await webhook.send(content="Hello from webhook!")
```

### Сообщение с именем и аватаром

```python
await webhook.send(
    content="Custom message",
    username="Custom Name",
    avatar_url="https://example.com/avatar.png"
)
```

### Сообщение с Embed

```python
from discordself import Embed

embed = Embed(
    title="Webhook Embed",
    description="This is from a webhook",
    color=0xff0000
)

await webhook.send(
    content="Check this embed!",
    embeds=[embed]
)
```

### Сообщение с файлами

```python
with open("image.png", "rb") as f:
    await webhook.send(
        content="Here's an image:",
        files=[{"file": f, "filename": "image.png"}]
    )
```

### Сообщение в нить

```python
await webhook.send(
    content="Message in thread",
    thread_id=thread_id
)
```

## Управление Webhooks

### Получить webhooks канала

```python
webhooks = await client.get_channel_webhooks(channel_id=123456789)
for webhook in webhooks:
    print(f"Webhook: {webhook['name']} (ID: {webhook['id']})")
```

### Получить webhooks гильдии

```python
webhooks = await client.get_guild_webhooks(guild_id=123456789)
```

### Удалить webhook

```python
await client.delete_webhook(webhook_id=webhook_id)
```

### Изменить webhook

```python
await client.modify_webhook(
    webhook_id=webhook_id,
    name="New Name",
    avatar="https://example.com/new_avatar.png"
)
```

## Примеры

### Система логирования

```python
class Logger:
    def __init__(self, webhook):
        self.webhook = webhook
    
    async def log(self, level, message):
        colors = {
            "INFO": 0x3498db,
            "WARNING": 0xf39c12,
            "ERROR": 0xe74c3c,
            "SUCCESS": 0x2ecc71
        }
        
        embed = Embed(
            title=f"{level}",
            description=message,
            color=colors.get(level, 0x95a5a6),
            timestamp=datetime.utcnow().isoformat()
        )
        
        await self.webhook.send(embeds=[embed])

# Использование
webhook = client.get_webhook(webhook_id, webhook_token)
logger = Logger(webhook)

await logger.log("INFO", "Бот запущен")
await logger.log("ERROR", "Произошла ошибка")
```

### Автоматические уведомления

```python
@client.event("guild_join")
async def on_guild_join(guild):
    webhook = client.get_webhook(NOTIFICATION_WEBHOOK_ID, NOTIFICATION_WEBHOOK_TOKEN)
    
    embed = Embed(
        title="Новая гильдия",
        description=f"Присоединился к {guild.name}",
        color=0x2ecc71
    )
    embed.add_field(name="Участников", value=guild.member_count)
    embed.add_field(name="ID", value=guild.id)
    
    await webhook.send(embeds=[embed])
```

### Форматирование сообщений

```python
async def send_formatted_message(webhook, title, fields):
    embed = Embed(title=title, color=0x3498db)
    
    for name, value in fields.items():
        embed.add_field(name=name, value=value, inline=False)
    
    await webhook.send(embeds=[embed])

# Использование
await send_formatted_message(
    webhook,
    "Информация о пользователе",
    {
        "Имя": user.username,
        "ID": user.id,
        "Создан": user.created_at
    }
)
```

## Best Practices

1. **Храните токены безопасно** - не публикуйте webhook токены
2. **Используйте разные webhooks** для разных целей
3. **Ограничивайте частоту** отправки сообщений
4. **Используйте embeds** для структурированных сообщений
5. **Обрабатывайте ошибки** при отправке

