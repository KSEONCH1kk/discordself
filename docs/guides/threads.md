# Threads - Нитки

DiscordSelf поддерживает полную работу с нитями (threads) Discord.

## Создание нитей

### Создать нить из сообщения

```python
thread = await client.start_thread_with_message(
    channel_id=123456789,
    message_id=987654321,
    name="Обсуждение",
    auto_archive_duration=60  # Автоархивация через 60 минут
)
```

### Создать нить без сообщения

```python
thread = await client.start_thread_without_message(
    channel_id=123456789,
    name="Новая нить",
    auto_archive_duration=1440,  # 24 часа
    type=11,  # GUILD_PUBLIC_THREAD
    invitable=True  # Для приватных нитей
)
```

## Управление нитями

### Присоединиться к нити

```python
await client.join_thread(channel_id=thread_id)
```

### Покинуть нить

```python
await client.leave_thread(channel_id=thread_id)
```

### Добавить участника

```python
await client.add_thread_member(channel_id=thread_id, user_id=user_id)
```

### Удалить участника

```python
await client.remove_thread_member(channel_id=thread_id, user_id=user_id)
```

### Получить участника нити

```python
member = await client.get_thread_member(channel_id=thread_id, user_id=user_id)
```

### Получить всех участников

```python
members = await client.list_thread_members(channel_id=thread_id)
```

## Получение нитей

### Активные нити гильдии

```python
threads = await client.list_active_threads(guild_id=123456789)
for thread in threads["threads"]:
    print(f"Thread: {thread['name']}")
```

### Архивированные нити

```python
# Публичные архивированные
public_archived = await client.list_public_archived_threads(
    channel_id=123456789,
    before=None,
    limit=50
)

# Приватные архивированные
private_archived = await client.list_private_archived_threads(
    channel_id=123456789,
    before=None,
    limit=50
)

# Присоединенные приватные архивированные
joined_archived = await client.list_joined_private_archived_threads(
    channel_id=123456789,
    before=None,
    limit=50
)
```

## Отправка сообщений в нить

### Обычное сообщение

```python
await client.send_message(
    channel_id=thread_id,
    content="Сообщение в нити"
)
```

### С thread_id

```python
await client.send_message(
    channel_id=parent_channel_id,
    content="Сообщение",
    thread_id=thread_id
)
```

## Примеры

### Автоматическое создание нити

```python
@client.event("message")
async def on_message(message):
    # Если сообщение содержит ключевое слово, создать нить
    if "обсуждение" in message.content.lower():
        thread = await client.start_thread_with_message(
            channel_id=message.channel_id,
            message_id=message.id,
            name=f"Обсуждение: {message.content[:50]}",
            auto_archive_duration=1440
        )
        await message.channel.send(f"Создана нить: {thread['name']}")
```

### Управление нитями

```python
@bot.command(name="thread")
async def thread_command(ctx, action: str, thread_id: int = None):
    if action == "create":
        thread = await client.start_thread_without_message(
            channel_id=ctx.channel_id,
            name="Новая нить",
            auto_archive_duration=60
        )
        await ctx.send(f"Создана нить: {thread['name']}")
    
    elif action == "join":
        if thread_id:
            await client.join_thread(channel_id=thread_id)
            await ctx.send("Присоединился к нити")
        else:
            await ctx.send("Укажите ID нити")
    
    elif action == "leave":
        if thread_id:
            await client.leave_thread(channel_id=thread_id)
            await ctx.send("Покинул нить")
        else:
            await ctx.send("Укажите ID нити")
```

### Мониторинг нитей

```python
@client.event("thread_create")
async def on_thread_create(thread):
    print(f"Создана нить: {thread.name} в канале {thread.parent_id}")

@client.event("thread_update")
async def on_thread_update(before, after):
    if before.name != after.name:
        print(f"Нить переименована: {before.name} -> {after.name}")

@client.event("thread_delete")
async def on_thread_delete(thread):
    print(f"Нить удалена: {thread.name}")
```

## Best Practices

1. **Используйте auto_archive_duration** для автоматической архивации
2. **Присоединяйтесь к нитям** перед отправкой сообщений
3. **Мониторьте активные нити** для управления
4. **Используйте правильный тип** нити (публичная/приватная)
5. **Ограничивайте количество нитей** для производительности

