# Продвинутые примеры

## Система уровней

```python
from discordself.commands import Bot
from discordself import Embed
import json

class LevelSystem:
    def __init__(self):
        self.users = {}  # {user_id: {"xp": 0, "level": 1}}
        self.load_data()
    
    def load_data(self):
        try:
            with open("levels.json", "r") as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}
    
    def save_data(self):
        with open("levels.json", "w") as f:
            json.dump(self.users, f)
    
    def add_xp(self, user_id, xp):
        if user_id not in self.users:
            self.users[user_id] = {"xp": 0, "level": 1}
        
        self.users[user_id]["xp"] += xp
        
        # Проверить повышение уровня
        new_level = self.calculate_level(self.users[user_id]["xp"])
        if new_level > self.users[user_id]["level"]:
            self.users[user_id]["level"] = new_level
            self.save_data()
            return new_level
        else:
            self.save_data()
            return None
    
    def calculate_level(self, xp):
        return int(xp ** 0.5 / 10) + 1

level_system = LevelSystem()

@bot.command(name="level")
async def level_command(ctx):
    user_id = str(ctx.author.id)
    if user_id not in level_system.users:
        await ctx.send("У вас еще нет опыта!")
        return
    
    user_data = level_system.users[user_id]
    embed = Embed(
        title=f"Уровень {ctx.author.username}",
        color=0x3498db
    )
    embed.add_field(name="Уровень", value=user_data["level"])
    embed.add_field(name="Опыт", value=user_data["xp"])
    await ctx.send(embed=embed)

@client.event("message")
async def on_message(message):
    if message.author.bot:
        return
    
    # Добавить опыт
    level_up = level_system.add_xp(str(message.author.id), 10)
    
    if level_up:
        await message.channel.send(
            f"🎉 {message.author.mention} повысил уровень до {level_up}!"
        )
```

## Экономическая система

```python
import json
from discordself.commands import Bot

class Economy:
    def __init__(self):
        self.balances = {}
        self.load_data()
    
    def load_data(self):
        try:
            with open("economy.json", "r") as f:
                self.balances = json.load(f)
        except FileNotFoundError:
            self.balances = {}
    
    def save_data(self):
        with open("economy.json", "w") as f:
            json.dump(self.balances, f)
    
    def get_balance(self, user_id):
        return self.balances.get(str(user_id), 0)
    
    def add_money(self, user_id, amount):
        user_id = str(user_id)
        if user_id not in self.balances:
            self.balances[user_id] = 0
        self.balances[user_id] += amount
        self.save_data()
    
    def remove_money(self, user_id, amount):
        user_id = str(user_id)
        if user_id not in self.balances:
            return False
        if self.balances[user_id] < amount:
            return False
        self.balances[user_id] -= amount
        self.save_data()
        return True

economy = Economy()

@bot.command(name="balance")
async def balance_command(ctx):
    balance = economy.get_balance(ctx.author.id)
    await ctx.send(f"💰 Ваш баланс: {balance} монет")

@bot.command(name="daily")
async def daily_command(ctx):
    economy.add_money(ctx.author.id, 100)
    await ctx.send("✅ Вы получили 100 монет!")

@bot.command(name="transfer")
async def transfer_command(ctx, user: UserConverter, amount: int):
    if amount <= 0:
        await ctx.send("❌ Сумма должна быть положительной!")
        return
    
    if not economy.remove_money(ctx.author.id, amount):
        await ctx.send("❌ Недостаточно средств!")
        return
    
    economy.add_money(user.id, amount)
    await ctx.send(f"✅ Переведено {amount} монет пользователю {user.mention}")
```

## Система тикетов

```python
from discordself.commands import Bot
from discordself import Embed

class TicketSystem:
    def __init__(self, client, guild_id):
        self.client = client
        self.guild_id = guild_id
        self.tickets = {}  # {ticket_id: {"user_id": ..., "channel_id": ...}}
    
    async def create_ticket(self, user_id):
        # Создать канал для тикета
        channel = await self.client.create_channel(
            guild_id=self.guild_id,
            name=f"ticket-{user_id}",
            type=0  # TEXT_CHANNEL
        )
        
        ticket_id = channel.id
        self.tickets[ticket_id] = {
            "user_id": user_id,
            "channel_id": ticket_id
        }
        
        # Отправить приветственное сообщение
        embed = Embed(
            title="Тикет создан",
            description="Опишите вашу проблему, и модератор поможет вам.",
            color=0x2ecc71
        )
        await self.client.send_message(
            channel_id=ticket_id,
            embeds=[embed]
        )
        
        return ticket_id

ticket_system = TicketSystem(client, guild_id)

@bot.command(name="ticket")
async def ticket_command(ctx):
    ticket_id = await ticket_system.create_ticket(ctx.author.id)
    await ctx.send(f"✅ Тикет создан: <#{ticket_id}>")

@bot.command(name="close")
async def close_ticket(ctx):
    if ctx.channel_id in ticket_system.tickets:
        await ctx.send("Тикет закрывается...")
        await asyncio.sleep(2)
        await self.client.delete_channel(ctx.channel_id)
        del ticket_system.tickets[ctx.channel_id]
```

## Система ролей по реакции

```python
from discordself.commands import Bot

ROLE_MESSAGE_ID = 123456789
ROLES = {
    "🎮": 111111111,  # Gamer role
    "🎵": 222222222,  # Music role
    "💻": 333333333,  # Developer role
}

@client.event("reaction_add")
async def on_reaction_add(reaction, user):
    if reaction.message.id == ROLE_MESSAGE_ID:
        emoji = str(reaction.emoji)
        if emoji in ROLES:
            role_id = ROLES[emoji]
            await client.add_role(
                guild_id=reaction.message.guild_id,
                user_id=user.id,
                role_id=role_id
            )
            await reaction.message.channel.send(
                f"✅ {user.mention} получил роль!"
            )

@client.event("reaction_remove")
async def on_reaction_remove(reaction, user):
    if reaction.message.id == ROLE_MESSAGE_ID:
        emoji = str(reaction.emoji)
        if emoji in ROLES:
            role_id = ROLES[emoji]
            await client.remove_role(
                guild_id=reaction.message.guild_id,
                user_id=user.id,
                role_id=role_id
            )
            await reaction.message.channel.send(
                f"❌ {user.mention} потерял роль!"
            )

@bot.command(name="roles")
async def roles_command(ctx):
    embed = Embed(
        title="Роли по реакциям",
        description="Нажмите на реакцию, чтобы получить роль:",
        color=0x3498db
    )
    embed.add_field(name="🎮", value="Gamer", inline=True)
    embed.add_field(name="🎵", value="Music", inline=True)
    embed.add_field(name="💻", value="Developer", inline=True)
    
    message = await ctx.send(embed=embed)
    
    # Добавить реакции
    for emoji in ROLES.keys():
        await client.add_reaction(ctx.channel_id, message.id, emoji)
```

## Система модерации

```python
from discordself.commands import Bot, UserConverter
from discordself.checks import has_permissions
from discordself.permissions import Permissions
from discordself import Embed

@bot.command(name="warn")
@has_permissions(Permissions.MANAGE_MESSAGES)
async def warn_command(ctx, user: UserConverter, *, reason: str = "No reason"):
    # Сохранить предупреждение
    # save_warning(user.id, reason, ctx.author.id)
    
    embed = Embed(
        title="Предупреждение",
        description=f"{user.mention} получил предупреждение",
        color=0xf39c12
    )
    embed.add_field(name="Причина", value=reason)
    embed.add_field(name="Модератор", value=ctx.author.mention)
    
    await ctx.send(embed=embed)
    
    # Отправить в DM
    try:
        await client.send_message(
            channel_id=user.id,  # DM channel
            embed=embed
        )
    except:
        pass

@bot.command(name="warnings")
async def warnings_command(ctx, user: UserConverter = None):
    target = user or ctx.author
    # Получить предупреждения
    # warnings = get_warnings(target.id)
    
    embed = Embed(
        title=f"Предупреждения {target.username}",
        color=0xe74c3c
    )
    # for warning in warnings:
    #     embed.add_field(name=warning["reason"], value=warning["date"])
    
    await ctx.send(embed=embed)
```

## Автоматическая модерация

```python
@client.event("message")
async def on_message(message):
    if message.author.bot:
        return
    
    # Проверка на спам
    if len(message.content) > 2000:
        await message.delete()
        await message.channel.send(
            f"{message.author.mention}, ваше сообщение слишком длинное!"
        )
        return
    
    # Проверка на капс
    if message.content.isupper() and len(message.content) > 10:
        await message.channel.send(
            f"{message.author.mention}, пожалуйста, не используйте капс!"
        )
    
    # Проверка на упоминания
    if len(message.mentions) > 5:
        await message.delete()
        await message.channel.send(
            f"{message.author.mention}, слишком много упоминаний!"
        )
```

