"""Пример Discord бота с кнопками"""

import asyncio
import logging
from discordself import Client, Intents, Button, ActionRow

# Включить логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

client = Client(
    token="MTQ0MzIzNzUyNTE0MDU0MTQ2MQ.Gq8rd-.ratCR_X2bK2gpNAwpMFCjiRNeRkMgrcBflipL8",
    intents=Intents.GUILDS | Intents.GUILD_MESSAGES | Intents.DIRECT_MESSAGES | Intents.MESSAGE_CONTENT
)


@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")
    print(f"📊 Серверов: {len(client.guilds)}")
    print(f"👥 Пользователь: {client.user.username}#{client.user.discriminator}")


@client.event("interaction_create")
async def on_interaction(interaction):
    """Обработка нажатий на кнопки"""
    print(f"🔘 Взаимодействие получено: {interaction.data}")
    
    if interaction.data.get("component_type") == 2:  # Button
        custom_id = interaction.data.get("custom_id")
        
        if custom_id == "btn1":
            await interaction.respond(
                content="✅ Вы нажали Кнопку 1!",
                ephemeral=True  # Только для пользователя
            )
            print("Нажата Кнопка 1")
        
        elif custom_id == "btn2":
            await interaction.respond(
                content="✅ Вы нажали Кнопку 2!",
                ephemeral=True
            )
            print("Нажата Кнопка 2")
        
        elif custom_id == "btn_danger":
            await interaction.respond(
                content="⚠️ Опасная кнопка нажата!",
                ephemeral=True
            )
            print("Нажата опасная кнопка")
        
        elif custom_id == "btn_success":
            await interaction.respond(
                content="🎉 Успешно выполнено!",
                ephemeral=True
            )
            print("Нажата кнопка успеха")
        
        elif custom_id == "btn_link":
            # Link кнопки не отправляют interaction
            pass


async def send_buttons_basic(channel_id: int):
    """Отправить сообщение с базовыми кнопками"""
    button1 = Button(
        Button.STYLE_PRIMARY,
        label="Кнопка 1",
        custom_id="btn1"
    )
    
    button2 = Button(
        Button.STYLE_SECONDARY,
        label="Кнопка 2",
        custom_id="btn2"
    )
    
    row = ActionRow()
    row.add_button(button1)
    row.add_button(button2)
    
    await client.send_message(
        channel_id=channel_id,
        content="Выберите действие:",
        components=[row]
    )
    
    print("✅ Отправлено сообщение с базовыми кнопками")


async def send_buttons_advanced(channel_id: int):
    """Отправить сообщение с продвинутыми кнопками"""
    # Первый ряд кнопок
    row1 = ActionRow()
    
    btn_primary = Button(
        Button.STYLE_PRIMARY,
        label="Главная",
        custom_id="btn1",
        emoji="🏠"
    )
    
    btn_secondary = Button(
        Button.STYLE_SECONDARY,
        label="Инфо",
        custom_id="btn2",
        emoji="ℹ️"
    )
    
    btn_success = Button(
        Button.STYLE_SUCCESS,
        label="Успех",
        custom_id="btn_success",
        emoji="✅"
    )
    
    btn_danger = Button(
        Button.STYLE_DANGER,
        label="Опасно",
        custom_id="btn_danger",
        emoji="⚠️"
    )
    
    row1.add_button(btn_primary)
    row1.add_button(btn_secondary)
    row1.add_button(btn_success)
    row1.add_button(btn_danger)
    
    # Второй ряд с ссылкой
    row2 = ActionRow()
    
    btn_link = Button(
        Button.STYLE_LINK,
        label="Открыть GitHub",
        url="https://github.com"
    )
    
    row2.add_button(btn_link)
    
    await client.send_message(
        channel_id=channel_id,
        content="📋 **Расширенное меню с кнопками**\n\nВыберите действие из меню ниже:",
        components=[row1, row2]
    )
    
    print("✅ Отправлено сообщение с продвинутыми кнопками")


async def send_buttons_disabled(channel_id: int):
    """Отправить сообщение с отключенными кнопками"""
    row = ActionRow()
    
    btn_enabled = Button(
        Button.STYLE_PRIMARY,
        label="Активная",
        custom_id="btn_enabled"
    )
    
    btn_disabled = Button(
        Button.STYLE_SECONDARY,
        label="Отключена",
        custom_id="btn_disabled",
        disabled=True
    )
    
    row.add_button(btn_enabled)
    row.add_button(btn_disabled)
    
    await client.send_message(
        channel_id=channel_id,
        content="Пример с отключенной кнопкой:",
        components=[row]
    )
    
    print("✅ Отправлено сообщение с отключенной кнопкой")


async def send_buttons_grid(channel_id: int):
    """Отправить сообщение с сеткой кнопок (несколько рядов)"""
    # Создаем 5 рядов по 5 кнопок
    rows = []
    
    for row_num in range(5):
        row = ActionRow()
        for btn_num in range(5):
            button_id = row_num * 5 + btn_num + 1
            btn = Button(
                Button.STYLE_SECONDARY,
                label=f"{button_id}",
                custom_id=f"btn_grid_{button_id}"
            )
            row.add_button(btn)
        rows.append(row)
    
    await client.send_message(
        channel_id=channel_id,
        content="🔢 Сетка кнопок 5x5:",
        components=rows
    )
    
    print("✅ Отправлена сетка кнопок")


async def main():
    async with client:
        print("🚀 Бот запущен!")
        
        # Укажите ID канала для отправки сообщений
        channel_id = 1400430682622394529  # Замените на ваш ID канала
        
        # Подождать готовности
        await asyncio.sleep(2)
        
        # Отправить разные примеры кнопок
        await send_buttons_basic(channel_id)
        await asyncio.sleep(1)
        
        await send_buttons_advanced(channel_id)
        await asyncio.sleep(1)
        
        await send_buttons_disabled(channel_id)
        await asyncio.sleep(1)
        
        await send_buttons_grid(channel_id)
        
        # Держать бота запущенным для обработки interaction
        print("⏳ Ожидание взаимодействий с кнопками...")
        await asyncio.sleep(3600 * 24)  # 24 часа


if __name__ == "__main__":
    asyncio.run(main())