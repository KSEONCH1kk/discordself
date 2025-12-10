"""Расширенные примеры использования DiscordSelf библиотеки"""

import asyncio
import os
from discordself import (
    Client, Status, Embed, Button, ActionRow,
    create_embed, create_button, create_action_row
)

TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_TOKEN_HERE")
client = Client(token=TOKEN)


@client.event("ready")
async def on_ready():
    print(f"✅ Logged in as {client.user}")


@client.event("message")
async def on_message(message):
    """Примеры расширенного использования"""
    
    # Игнорировать сообщения от ботов
    if message.author.bot:
        return
    
    # Пример 1: Отправка сообщения с embed
    if message.content == "!embed":
        embed = create_embed(
            title="Пример Embed",
            description="Это пример embed сообщения",
            color=0x00ff00
        )
        embed.set_author(name="DiscordSelf", icon_url="https://discord.com/assets/f9bb9c4af2b9c32a2c5ee0014661546d.png")
        embed.add_field(name="Поле 1", value="Значение 1", inline=True)
        embed.add_field(name="Поле 2", value="Значение 2", inline=True)
        embed.set_footer(text="Footer текст")
        
        await message.channel.send(embeds=[embed])
    
    # Пример 2: Отправка сообщения с кнопками
    elif message.content == "!buttons":
        button1 = create_button(
            Button.STYLE_PRIMARY,
            label="Кнопка 1",
            custom_id="button_1"
        )
        button2 = create_button(
            Button.STYLE_SECONDARY,
            label="Кнопка 2",
            custom_id="button_2"
        )
        button3 = create_button(
            Button.STYLE_DANGER,
            label="Удалить",
            custom_id="button_delete"
        )
        
        row = create_action_row()
        row.add_button(button1)
        row.add_button(button2)
        row.add_button(button3)
        
        await message.channel.send(
            content="Выберите действие:",
            components=[row]
        )
    
    # Пример 3: Отправка сообщения в стиле webhook
    elif message.content == "!webhook":
        embed = Embed(
            title="Webhook стиль",
            description="Сообщение отправлено через обычный API, но выглядит как webhook",
            color=0xff0000
        )
        
        await message.channel.send(
            content="**Внимание!**",
            embeds=[embed],
            allowed_mentions={"parse": []}  # Без упоминаний
        )
    
    # Пример 4: Чтение всех сообщений канала
    elif message.content == "!readall":
        messages = await message.channel.fetch_all_messages(limit=100)
        await message.channel.send(f"Найдено {len(messages)} сообщений")
    
    # Пример 5: Поиск сообщений
    elif message.content.startswith("!search "):
        query = message.content[8:]
        if message.guild:
            results = await client.search_messages(
                guild_id=message.guild.id,
                has=query,
                limit=10
            )
            await message.channel.send(f"Найдено сообщений: {results.get('total_results', 0)}")
    
    # Пример 6: Массовое чтение с фильтром
    elif message.content == "!readfiltered":
        def check(msg_data):
            # Фильтр: только сообщения с текстом длиннее 10 символов
            return len(msg_data.get("content", "")) > 10
        
        messages = await message.channel.fetch_all_messages(
            limit=50,
            check=check
        )
        await message.channel.send(f"Найдено {len(messages)} сообщений (фильтр: длина > 10)")
    
    # Пример 7: Редактирование сообщения с embed
    elif message.content == "!editembed":
        msg = await message.channel.send("Оригинальное сообщение")
        
        await asyncio.sleep(2)
        
        embed = Embed(
            title="Отредактированное сообщение",
            description="Это сообщение было отредактировано",
            color=0x0000ff
        )
        
        await msg.edit(
            content="",
            embeds=[embed]
        )
    
    # Пример 8: Работа с реакциями
    elif message.content == "!react":
        await message.add_reaction("👍")
        await message.add_reaction("❤️")
        await message.add_reaction("🔥")
    
    # Пример 9: Получение всех реакций
    elif message.content.startswith("!getreacts"):
        # Реакции на предыдущее сообщение
        if message.referenced_message:
            reactions = await client.get_reactions(
                channel_id=message.channel_id,
                message_id=message.referenced_message.id,
                emoji="👍",
                limit=10
            )
            await message.channel.send(f"Найдено {len(reactions)} реакций 👍")


@client.event("raw_socket_receive")
async def on_raw_socket_receive(event_name, data):
    """Обработка сырых событий Gateway"""
    # Можно обрабатывать любые события напрямую
    if event_name == "MESSAGE_REACTION_ADD":
        print(f"Реакция добавлена: {data}")


async def main():
    try:
        async with client:
            print("🚀 Advanced client started. Press Ctrl+C to stop.")
            await asyncio.sleep(3600 * 24)
    except KeyboardInterrupt:
        print("\n⏹️  Stopping client...")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

