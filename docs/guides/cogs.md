# Cogs - Модульная организация

Cogs позволяют организовать команды и обработчики событий в отдельные модули.

## Базовое использование

### Создание Cog

```python
from discordself.cogs import Cog, command, listener

class MyCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @command(name="hello")
    async def hello_command(self, ctx):
        await ctx.send("Hello from Cog!")
    
    @listener("ready")
    async def on_ready(self):
        print("Cog loaded!")
```

### Загрузка Cog

```python
from discordself.cogs import CogManager

bot = Bot(client, command_prefix="!")

# Создать менеджер
cog_manager = CogManager(bot)

# Загрузить Cog
my_cog = MyCog(bot)
cog_manager.add_cog(my_cog)
```

## Жизненный цикл Cog

### cog_load()

Вызывается при загрузке Cog:

```python
class MyCog(Cog):
    async def cog_load(self):
        print("Cog загружается...")
        # Инициализация
```

### cog_unload()

Вызывается при выгрузке Cog:

```python
class MyCog(Cog):
    async def cog_unload(self):
        print("Cog выгружается...")
        # Очистка ресурсов
```

## Примеры

### Admin Cog

```python
from discordself.cogs import Cog, command
from discordself.checks import has_permissions
from discordself.permissions import Permissions
from discordself.commands import UserConverter

class AdminCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @command(name="ban")
    @has_permissions(Permissions.BAN_MEMBERS)
    async def ban_command(self, ctx, user: UserConverter, *, reason: str = "No reason"):
        await ctx.send(f"Would ban {user.mention} for: {reason}")
    
    @command(name="kick")
    @has_permissions(Permissions.KICK_MEMBERS)
    async def kick_command(self, ctx, user: UserConverter, *, reason: str = "No reason"):
        await ctx.send(f"Would kick {user.mention} for: {reason}")
    
    @command(name="mute")
    @has_permissions(Permissions.MUTE_MEMBERS)
    async def mute_command(self, ctx, user: UserConverter):
        await ctx.send(f"Would mute {user.mention}")

# Загрузка
admin_cog = AdminCog(bot)
bot.cog_manager.add_cog(admin_cog)
```

### Music Cog

```python
from discordself.cogs import Cog, command
from discordself.voice import VoiceClient
from discordself.ffmpeg import FFmpegOpusAudio

class MusicCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}  # Очереди для каждой гильдии
    
    @command(name="play")
    async def play_command(self, ctx, url: str):
        if not ctx.author.voice:
            await ctx.send("Вы должны быть в голосовом канале!")
            return
        
        channel = ctx.author.voice.channel
        
        # Подключиться
        if not ctx.guild.voice_client:
            voice_client = await channel.connect()
        else:
            voice_client = ctx.guild.voice_client
        
        # Воспроизвести
        source = FFmpegOpusAudio(url)
        voice_client.play(source)
        await ctx.send(f"Воспроизведение: {url}")
    
    @command(name="stop")
    async def stop_command(self, ctx):
        if ctx.guild.voice_client:
            ctx.guild.voice_client.stop()
            await ctx.send("Остановлено")
    
    @command(name="disconnect")
    async def disconnect_command(self, ctx):
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
            await ctx.send("Отключено")

# Загрузка
music_cog = MusicCog(bot)
bot.cog_manager.add_cog(music_cog)
```

### Utility Cog

```python
from discordself.cogs import Cog, command, listener
from discordself import Embed

class UtilityCog(Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @command(name="ping")
    async def ping_command(self, ctx):
        await ctx.send("🏓 Pong!")
    
    @command(name="info")
    async def info_command(self, ctx):
        embed = Embed(
            title="Информация о боте",
            description=f"Команд: {len(self.bot.commands)}",
            color=0x3498db
        )
        embed.add_field(name="Гильдий", value=len(ctx.bot.client.guilds))
        await ctx.send(embed=embed)
    
    @listener("message")
    async def on_message(self, message):
        # Обработка сообщений
        pass

# Загрузка
utility_cog = UtilityCog(bot)
bot.cog_manager.add_cog(utility_cog)
```

## Управление Cogs

### Загрузка

```python
cog = MyCog(bot)
bot.cog_manager.add_cog(cog)
```

### Выгрузка

```python
bot.cog_manager.remove_cog("MyCog")
```

### Перезагрузка

```python
bot.cog_manager.reload_cog("MyCog")
```

### Получить Cog

```python
cog = bot.cog_manager.get_cog("MyCog")
```

## Best Practices

1. **Разделяйте функциональность** по разным Cogs
2. **Используйте cog_load/cog_unload** для инициализации
3. **Храните состояние** в атрибутах класса
4. **Используйте listeners** для обработки событий
5. **Документируйте команды** через docstrings

