# Начало работы с DiscordSelf

## Установка

### Требования

- Python 3.8 или выше
- pip

### Установка через pip

```bash
pip install discordself
```

### Установка из исходников

```bash
git clone https://github.com/yourusername/discordself.git
cd discordself
pip install -r requirements.txt
```

### Зависимости

- `aiohttp>=3.8.0,<4.0.0` - HTTP клиент
- `websockets>=10.0` - WebSocket клиент
- `pynacl>=1.5.0` - Криптография для голоса
- `opuslib>=3.0.0` - Opus кодирование
- `yt-dlp>=2023.0.0` - YouTube поддержка (опционально)

## Быстрый старт

### Минимальный пример

```python
import asyncio
from discordself import Client, Intents

# Создать клиент
client = Client(
    token="YOUR_TOKEN_HERE",
    intents=Intents.GUILD_MESSAGES | Intents.MESSAGE_CONTENT
)

# Обработчик события ready
@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")

# Обработчик сообщений
@client.event("message")
async def on_message(message):
    if message.content == "!ping":
        await message.channel.send("🏓 Pong!")

# Запуск
async def main():
    async with client:
        await asyncio.sleep(3600)  # Работать 1 час

if __name__ == "__main__":
    asyncio.run(main())
```

### Получение токена

1. Откройте Discord в браузере
2. Нажмите F12 для открытия DevTools
3. Перейдите в Network
4. Отправьте любое сообщение
5. Найдите запрос к `discord.com/api` и откройте его
6. В Headers найдите `authorization` - это ваш токен

⚠️ **Важно**: Никогда не публикуйте свой токен! Храните его в переменных окружения или конфигурационных файлах.

### Использование переменных окружения

```python
import os
from discordself import Client

token = os.getenv("DISCORD_TOKEN")
client = Client(token=token)
```

## Основные концепции

### Client

`Client` - основной класс для взаимодействия с Discord API. Он управляет:
- HTTP запросами
- WebSocket соединением
- Кэшированием объектов
- Обработкой событий

### Intents

Intents определяют, какие события вы хотите получать от Discord:

```python
from discordself import Intents

# Базовые intents
intents = Intents.GUILD_MESSAGES | Intents.MESSAGE_CONTENT

# Все intents (может не работать для обычных ботов)
intents = Intents.ALL

# Комбинация intents
intents = Intents.calculate(
    Intents.GUILDS,
    Intents.GUILD_MESSAGES,
    Intents.DIRECT_MESSAGES
)
```

### События

События обрабатываются через декоратор `@client.event()`:

```python
@client.event("ready")
async def on_ready():
    print("Бот готов!")

@client.event("message")
async def on_message(message):
    print(f"Новое сообщение: {message.content}")
```

### Асинхронность

Все операции в DiscordSelf асинхронные. Используйте `async/await`:

```python
# ✅ Правильно
async def send_message():
    await client.send_message(channel_id=123, content="Hello")

# ❌ Неправильно
def send_message():
    client.send_message(channel_id=123, content="Hello")  # Не сработает
```

## Следующие шаги

- [Система команд](guides/commands.md) - Создание команд с автоматическим парсингом
- [Работа с событиями](guides/events.md) - Обработка событий Discord
- [API Reference](api-reference.md) - Полная документация API

