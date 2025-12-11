# Tasks - Фоновые задачи

DiscordSelf поддерживает создание фоновых задач, которые выполняются периодически.

## Создание задачи

### Базовый пример

```python
from discordself.tasks import Loop

@Loop(seconds=60)  # Выполнять каждые 60 секунд
async def my_task():
    print("Задача выполнена!")

# Запустить задачу
my_task.start()
```

### Задача с доступом к клиенту

```python
from discordself.tasks import Loop

@Loop(seconds=300)  # Каждые 5 минут
async def status_update():
    # Изменить статус
    await client.change_presence(
        status=Status.ONLINE,
        activities=[{
            "name": f"Серверов: {len(client.guilds)}",
            "type": 0
        }]
    )

# Запустить после ready
@client.event("ready")
async def on_ready():
    status_update.start()
```

## Параметры Loop

### Интервалы

```python
@Loop(seconds=60)      # Каждые 60 секунд
@Loop(minutes=5)       # Каждые 5 минут
@Loop(hours=1)         # Каждый час
@Loop(count=10)        # Выполнить 10 раз
```

### Условия

```python
@Loop(seconds=60, count=10)  # Выполнить 10 раз с интервалом 60 секунд
async def limited_task():
    print("Ограниченная задача")
```

## Управление задачами

### Запуск

```python
task = Loop(seconds=60)(my_function)
task.start()
```

### Остановка

```python
task.stop()
```

### Перезапуск

```python
task.restart()
```

### Проверка состояния

```python
if task.is_running():
    print("Задача выполняется")
```

## Примеры

### Обновление статистики

```python
@Loop(minutes=5)
async def update_stats():
    stats_channel = await client.fetch_channel(STATS_CHANNEL_ID)
    
    embed = Embed(
        title="Статистика бота",
        color=0x3498db
    )
    embed.add_field(name="Серверов", value=len(client.guilds))
    embed.add_field(name="Пользователей", value=sum(g.member_count for g in client.guilds.values()))
    
    await stats_channel.send(embed=embed)

@client.event("ready")
async def on_ready():
    update_stats.start()
```

### Очистка данных

```python
@Loop(hours=24)
async def cleanup():
    # Очистить старые данные
    # cleanup_old_data()
    print("Очистка выполнена")

cleanup.start()
```

### Периодические уведомления

```python
@Loop(hours=1)
async def hourly_reminder():
    channel = await client.fetch_channel(REMINDER_CHANNEL_ID)
    await channel.send("⏰ Напоминание каждый час!")

hourly_reminder.start()
```

## Best Practices

1. **Используйте разумные интервалы** - не слишком часто
2. **Обрабатывайте ошибки** в задачах
3. **Останавливайте задачи** при закрытии клиента
4. **Используйте count** для ограниченных задач
5. **Логируйте выполнение** для отладки

