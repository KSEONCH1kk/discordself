# Работа с событиями

DiscordSelf предоставляет систему событий для обработки различных действий в Discord.

## Регистрация обработчиков

### Декоратор @client.event()

```python
@client.event("ready")
async def on_ready():
    print("Бот готов!")

@client.event("message")
async def on_message(message):
    print(f"Новое сообщение: {message.content}")
```

### Декоратор @client.listen()

```python
@client.listen("message")
async def on_message(message):
    print(f"Сообщение: {message.content}")

# С приоритетом
@client.listen("message", priority=1)
async def on_message_high_priority(message):
    print("Высокий приоритет!")
```

## Доступные события

### События соединения

#### `ready`
Вызывается когда клиент готов к работе.

```python
@client.event("ready")
async def on_ready():
    print(f"Logged in as {client.user}")
    print(f"Connected to {len(client.guilds)} guilds")
```

### События сообщений

#### `message` / `message_create`
Новое сообщение.

```python
@client.event("message")
async def on_message(message):
    if message.author.bot:
        return
    
    print(f"{message.author}: {message.content}")
```

#### `message_update`
Сообщение обновлено.

```python
@client.event("message_update")
async def on_message_update(before, after):
    if before.content != after.content:
        print(f"Сообщение изменено: {before.content} -> {after.content}")
```

#### `message_delete`
Сообщение удалено.

```python
@client.event("message_delete")
async def on_message_delete(message):
    print(f"Сообщение удалено: {message.content}")
```

### События гильдий

#### `guild_join`
Присоединение к гильдии.

```python
@client.event("guild_join")
async def on_guild_join(guild):
    print(f"Присоединился к {guild.name}")
```

#### `guild_update`
Обновление гильдии.

```python
@client.event("guild_update")
async def on_guild_update(before, after):
    if before.name != after.name:
        print(f"Гильдия переименована: {before.name} -> {after.name}")
```

#### `guild_remove`
Покидание гильдии.

```python
@client.event("guild_remove")
async def on_guild_remove(guild):
    print(f"Покинул {guild.name}")
```

### События каналов

#### `channel_create`
Создание канала.

```python
@client.event("channel_create")
async def on_channel_create(channel):
    print(f"Создан канал: {channel.name}")
```

#### `channel_update`
Обновление канала.

```python
@client.event("channel_update")
async def on_channel_update(before, after):
    if before.name != after.name:
        print(f"Канал переименован: {before.name} -> {after.name}")
```

#### `channel_delete`
Удаление канала.

```python
@client.event("channel_delete")
async def on_channel_delete(channel):
    print(f"Удален канал: {channel.name}")
```

### События голоса

#### `voice_state_update`
Изменение голосового состояния.

```python
@client.event("voice_state_update")
async def on_voice_state_update(before, after):
    if before.channel != after.channel:
        if after.channel:
            print(f"{after.user} присоединился к {after.channel.name}")
        else:
            print(f"{before.user} покинул {before.channel.name}")
```

### События interactions

#### `interaction_create`
Создание interaction.

```python
@client.event("interaction_create")
async def on_interaction_create(interaction):
    print(f"Interaction: {interaction.type}")
```

#### `modal_submit`
Отправка модального окна.

```python
@client.event("modal_submit")
async def on_modal_submit(interaction):
    value = interaction.get_modal_value("input_field")
    print(f"Modal value: {value}")
```

#### `component_interaction`
Взаимодействие с компонентом (кнопка, меню).

```python
@client.event("component_interaction")
async def on_component_interaction(interaction):
    print(f"Component clicked: {interaction.data.get('custom_id')}")
```

### События AutoMod

#### `automod_action_execution`
Выполнение действия AutoMod.

```python
@client.event("automod_action_execution")
async def on_automod_action(action):
    print(f"AutoMod action: {action.action}")
    print(f"Rule: {action.rule_id}")
    print(f"User: {action.user}")
```

## Ожидание событий

### wait_for()

Ожидать конкретное событие:

```python
# Ожидать сообщение от конкретного пользователя
message = await client.wait_for(
    "message",
    check=lambda m: m.author.id == 123456789,
    timeout=60
)
print(f"Получено: {message.content}")
```

### Примеры использования

#### Ожидание реакции

```python
def check_reaction(reaction, user):
    return reaction.emoji == "✅" and user.id == 123456789

reaction, user = await client.wait_for(
    "reaction_add",
    check=check_reaction,
    timeout=60
)
```

#### Ожидание команды подтверждения

```python
@bot.command(name="confirm")
async def confirm_command(ctx):
    await ctx.send("Подтвердите действие (✅/❌)")
    
    def check(reaction, user):
        return user == ctx.author and reaction.emoji in ["✅", "❌"]
    
    try:
        reaction, user = await client.wait_for(
            "reaction_add",
            check=check,
            timeout=30
        )
        
        if reaction.emoji == "✅":
            await ctx.send("Подтверждено!")
        else:
            await ctx.send("Отменено!")
    except asyncio.TimeoutError:
        await ctx.send("Время истекло!")
```

## Приоритеты обработчиков

Обработчики с более высоким приоритетом выполняются первыми:

```python
@client.listen("message", priority=2)
async def handler1(message):
    print("Handler 1 (priority 2)")

@client.listen("message", priority=1)
async def handler2(message):
    print("Handler 2 (priority 1)")

@client.listen("message", priority=0)  # По умолчанию
async def handler3(message):
    print("Handler 3 (priority 0)")
```

## Обработка ошибок в событиях

```python
@client.event("message")
async def on_message(message):
    try:
        # Ваш код
        pass
    except Exception as e:
        print(f"Ошибка в обработчике: {e}")
        import traceback
        traceback.print_exc()
```

## Best Practices

1. **Проверяйте автора сообщений** чтобы избежать бесконечных циклов:
   ```python
   @client.event("message")
   async def on_message(message):
       if message.author == client.user:
           return
   ```

2. **Используйте wait_for для интерактивности** вместо постоянных проверок

3. **Обрабатывайте ошибки** в обработчиках событий

4. **Используйте приоритеты** для контроля порядка выполнения

5. **Не блокируйте event loop** - используйте async/await

