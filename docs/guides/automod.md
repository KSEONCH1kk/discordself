# AutoMod

DiscordSelf поддерживает работу с AutoMod (автоматической модерацией) Discord.

## Получение правил

### Все правила гильдии

```python
rules = await client.get_automod_rules(guild_id=123456789)
for rule in rules:
    print(f"Rule: {rule['name']} (ID: {rule['id']})")
```

### Правило по ID

```python
rule = await client.get_automod_rule(guild_id=123456789, rule_id=rule_id)
print(f"Rule: {rule['name']}")
print(f"Enabled: {rule['enabled']}")
```

## Создание правил

### Правило с ключевыми словами

```python
from discordself.enums import AutoModEventType, AutoModTriggerType, AutoModActionType

rule = await client.create_automod_rule(
    guild_id=123456789,
    name="Блокировка мата",
    event_type=AutoModEventType.MESSAGE_SEND,
    trigger_type=AutoModTriggerType.KEYWORD,
    trigger_metadata={
        "keyword_filter": ["мат", "плохое слово"]
    },
    actions=[
        {
            "type": AutoModActionType.BLOCK_MESSAGE
        }
    ],
    enabled=True
)
```

### Правило с пресетом ключевых слов

```python
rule = await client.create_automod_rule(
    guild_id=123456789,
    name="Блокировка спама",
    event_type=AutoModEventType.MESSAGE_SEND,
    trigger_type=AutoModTriggerType.KEYWORD_PRESET,
    trigger_metadata={
        "presets": ["PROFANITY", "SEXUAL_CONTENT", "SLURS"]
    },
    actions=[
        {
            "type": AutoModActionType.BLOCK_MESSAGE
        },
        {
            "type": AutoModActionType.SEND_ALERT_MESSAGE,
            "metadata": {
                "channel_id": alert_channel_id
            }
        }
    ],
    enabled=True
)
```

### Правило с таймаутом

```python
rule = await client.create_automod_rule(
    guild_id=123456789,
    name="Спам защита",
    event_type=AutoModEventType.MESSAGE_SEND,
    trigger_type=AutoModTriggerType.SPAM,
    actions=[
        {
            "type": AutoModActionType.TIMEOUT,
            "metadata": {
                "duration_seconds": 300  # 5 минут
            }
        }
    ],
    enabled=True
)
```

### Правило с исключениями

```python
rule = await client.create_automod_rule(
    guild_id=123456789,
    name="Модерация",
    event_type=AutoModEventType.MESSAGE_SEND,
    trigger_type=AutoModTriggerType.KEYWORD,
    trigger_metadata={
        "keyword_filter": ["плохое слово"]
    },
    actions=[
        {
            "type": AutoModActionType.BLOCK_MESSAGE
        }
    ],
    enabled=True,
    exempt_roles=[moderator_role_id],  # Исключить модераторов
    exempt_channels=[admin_channel_id]  # Исключить админ канал
)
```

## Изменение правил

### Изменить правило

```python
updated_rule = await client.modify_automod_rule(
    guild_id=123456789,
    rule_id=rule_id,
    name="Новое название",
    enabled=False,  # Отключить правило
    trigger_metadata={
        "keyword_filter": ["новое", "слово"]
    }
)
```

### Обновить действия

```python
updated_rule = await client.modify_automod_rule(
    guild_id=123456789,
    rule_id=rule_id,
    actions=[
        {
            "type": AutoModActionType.BLOCK_MESSAGE
        },
        {
            "type": AutoModActionType.SEND_ALERT_MESSAGE,
            "metadata": {
                "channel_id": new_alert_channel_id
            }
        }
    ]
)
```

## Удаление правил

```python
await client.delete_automod_rule(guild_id=123456789, rule_id=rule_id)
```

## Обработка событий AutoMod

### Событие automod_action_execution

```python
@client.event("automod_action_execution")
async def on_automod_action(action):
    print(f"AutoMod action executed!")
    print(f"Rule ID: {action.rule_id}")
    print(f"User: {action.user}")
    print(f"Channel: {action.channel}")
    print(f"Content: {action.content}")
    print(f"Matched keyword: {action.matched_keyword}")
    
    # Логирование
    if action.action.get("type") == AutoModActionType.BLOCK_MESSAGE:
        print(f"Сообщение заблокировано: {action.content}")
```

### Логирование действий

```python
@client.event("automod_action_execution")
async def log_automod_action(action):
    embed = Embed(
        title="AutoMod Action",
        color=0xff0000,
        timestamp=datetime.utcnow().isoformat()
    )
    
    embed.add_field(name="Rule ID", value=action.rule_id)
    embed.add_field(name="User", value=action.user.mention if action.user else "Unknown")
    embed.add_field(name="Action", value=action.action.get("type"))
    embed.add_field(name="Content", value=action.content[:1000], inline=False)
    
    if action.matched_keyword:
        embed.add_field(name="Matched Keyword", value=action.matched_keyword)
    
    # Отправить в канал логирования
    await client.send_message(
        channel_id=LOG_CHANNEL_ID,
        embeds=[embed]
    )
```

## Примеры

### Система модерации

```python
class AutoModManager:
    def __init__(self, client, guild_id):
        self.client = client
        self.guild_id = guild_id
    
    async def setup_basic_rules(self):
        # Правило для мата
        await self.client.create_automod_rule(
            guild_id=self.guild_id,
            name="Блокировка мата",
            event_type=AutoModEventType.MESSAGE_SEND,
            trigger_type=AutoModTriggerType.KEYWORD_PRESET,
            trigger_metadata={
                "presets": ["PROFANITY"]
            },
            actions=[
                {
                    "type": AutoModActionType.BLOCK_MESSAGE
                }
            ],
            enabled=True
        )
        
        # Правило для спама
        await self.client.create_automod_rule(
            guild_id=self.guild_id,
            name="Защита от спама",
            event_type=AutoModEventType.MESSAGE_SEND,
            trigger_type=AutoModTriggerType.SPAM,
            actions=[
                {
                    "type": AutoModActionType.TIMEOUT,
                    "metadata": {
                        "duration_seconds": 600  # 10 минут
                    }
                }
            ],
            enabled=True
        )
    
    async def add_keyword_rule(self, name, keywords, action_type):
        await self.client.create_automod_rule(
            guild_id=self.guild_id,
            name=name,
            event_type=AutoModEventType.MESSAGE_SEND,
            trigger_type=AutoModTriggerType.KEYWORD,
            trigger_metadata={
                "keyword_filter": keywords
            },
            actions=[
                {
                    "type": action_type
                }
            ],
            enabled=True
        )

# Использование
automod = AutoModManager(client, guild_id)
await automod.setup_basic_rules()
await automod.add_keyword_rule(
    "Блокировка рекламы",
    ["купить", "скидка", "промокод"],
    AutoModActionType.BLOCK_MESSAGE
)
```

### Мониторинг AutoMod

```python
@client.event("automod_action_execution")
async def monitor_automod(action):
    # Получить правило
    rule = await client.get_automod_rule(action.guild_id, action.rule_id)
    
    # Статистика
    stats = {
        "rule_name": rule["name"],
        "user": action.user.username if action.user else "Unknown",
        "action": action.action.get("type"),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Сохранить статистику
    # save_stats(stats)
    
    print(f"AutoMod: {stats['rule_name']} triggered by {stats['user']}")
```

## Best Practices

1. **Используйте пресеты** для стандартных случаев
2. **Добавляйте исключения** для модераторов и админ каналов
3. **Логируйте действия** для мониторинга
4. **Тестируйте правила** перед включением
5. **Регулярно обновляйте** списки ключевых слов

