# FAQ - Часто задаваемые вопросы

## Общие вопросы

### Что такое DiscordSelf?

DiscordSelf - это библиотека для создания Discord selfbot на Python. Она позволяет автоматизировать действия вашего личного Discord аккаунта.

### Это безопасно?

⚠️ **Важно**: Использование selfbot нарушает Terms of Service Discord. Используйте на свой риск. Discord может заблокировать ваш аккаунт за использование selfbot.

### Чем DiscordSelf отличается от discord.py?

- **discord.py** - для создания ботов (использует Bot Token)
- **DiscordSelf** - для selfbot (использует User Token)

DiscordSelf специально разработан для работы с пользовательскими аккаунтами.

## Установка и настройка

### Как установить DiscordSelf?

```bash
pip install discordself
```

### Какие версии Python поддерживаются?

Python 3.8 или выше.

### Как получить токен?

1. Откройте Discord в браузере
2. Нажмите F12 для DevTools
3. Перейдите в Network
4. Отправьте сообщение
5. Найдите запрос к `discord.com/api`
6. В Headers найдите `authorization`

⚠️ **Никогда не публикуйте свой токен!**

### Как использовать переменные окружения?

```python
import os
from discordself import Client

token = os.getenv("DISCORD_TOKEN")
client = Client(token=token)
```

## Использование

### Как отправить сообщение?

```python
await client.send_message(channel_id=123456789, content="Hello!")
```

### Как получить сообщения канала?

```python
messages = await client.fetch_messages(channel_id=123456789, limit=50)
```

### Как обработать событие?

```python
@client.event("message")
async def on_message(message):
    print(f"New message: {message.content}")
```

### Как создать команду?

```python
from discordself.commands import Bot

bot = Bot(client, command_prefix="!")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong!")
```

## Проблемы и решения

### Ошибка "Invalid token"

- Проверьте, что токен правильный
- Убедитесь, что используете User Token, а не Bot Token
- Токен может быть устаревшим - получите новый

### Ошибка "Missing intents"

Добавьте необходимые intents:

```python
from discordself import Intents

client = Client(
    token=token,
    intents=Intents.GUILD_MESSAGES | Intents.MESSAGE_CONTENT
)
```

### Команды не работают

1. Убедитесь, что intents включены:
   ```python
   intents = Intents.GUILD_MESSAGES | Intents.MESSAGE_CONTENT
   ```

2. Проверьте, что префикс правильный

3. Убедитесь, что обработчик сообщений зарегистрирован

### Голос не работает

1. Убедитесь, что FFmpeg установлен
2. Проверьте наличие `opus.dll` (Windows)
3. Убедитесь, что вы подключены к голосовому каналу

### Rate limit ошибки

DiscordSelf автоматически обрабатывает rate limits. Если вы получаете ошибки:

1. Уменьшите частоту запросов
2. Используйте кэширование
3. Добавьте задержки между запросами

### WebSocket переподключение

DiscordSelf автоматически переподключается при разрыве соединения. Если проблемы продолжаются:

1. Проверьте интернет-соединение
2. Убедитесь, что токен валиден
3. Проверьте логи на наличие ошибок

## Best Practices

### Безопасность

1. **Никогда не публикуйте токен**
2. Используйте переменные окружения
3. Не коммитьте токены в Git
4. Регулярно обновляйте токен

### Производительность

1. Используйте кэширование
2. Ограничивайте частоту запросов
3. Используйте шардирование для больших ботов
4. Оптимизируйте обработчики событий

### Код

1. Используйте async/await правильно
2. Обрабатывайте ошибки
3. Логируйте важные события
4. Документируйте код

## Ограничения

### Что можно делать?

- Автоматизация личного аккаунта
- Образовательные цели
- Тестирование

### Что нельзя делать?

- Спам
- Нарушение правил Discord
- Массовая рассылка
- Любые незаконные действия

## Поддержка

### Где получить помощь?

- GitHub Issues
- Discord сервер (если есть)
- Документация

### Как сообщить об ошибке?

1. Проверьте, что ошибка воспроизводится
2. Соберите информацию:
   - Версия Python
   - Версия DiscordSelf
   - Трассировка ошибки
   - Минимальный пример кода
3. Создайте Issue на GitHub

## Частые ошибки

### AttributeError: 'NoneType' object has no attribute 'send'

Канал не найден в кэше. Используйте:

```python
channel = await client.fetch_channel(channel_id)
await channel.send("Hello!")
```

### TypeError: Object of type Embed is not JSON serializable

Преобразуйте Embed в словарь:

```python
embed_dict = embed.to_dict()
await client.send_message(channel_id=123, embeds=[embed_dict])
```

### CommandNotFound

Проверьте:
1. Правильность префикса
2. Регистр команды (если не case_insensitive)
3. Что команда зарегистрирована

### MissingRequiredArgument

Добавьте все обязательные аргументы или сделайте их опциональными:

```python
@bot.command(name="say")
async def say(ctx, *, text: str = "No text"):
    await ctx.send(text)
```

