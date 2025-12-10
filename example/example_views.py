"""Пример использования Views (UI Components)"""

import asyncio
from discordself import Client, Intents
from discordself.commands import Bot
from discordself.views import View, ButtonView, SelectMenuView, button
from discordself.embeds import Button, SelectMenu, Embed

client = Client(
    token="YOUR_TOKEN_HERE",
    intents=Intents.GUILDS
)

bot = Bot(client, command_prefix="!")


@bot.command(name="buttons")
async def show_buttons(ctx):
    """Показать кнопки"""
    view = ButtonView(timeout=60.0)
    
    # Создать кнопки
    btn1 = Button(label="Кнопка 1", style=1, custom_id="btn1")
    btn2 = Button(label="Кнопка 2", style=2, custom_id="btn2")
    btn3 = Button(label="Кнопка 3", style=3, custom_id="btn3")
    btn4 = Button(label="Ссылка", style=5, url="https://discord.com", custom_id="btn4")
    
    # Добавить обработчики
    async def on_btn1_click(interaction, button):
        await interaction.response.send_message("Вы нажали кнопку 1!")
    
    async def on_btn2_click(interaction, button):
        await interaction.response.send_message("Вы нажали кнопку 2!")
    
    async def on_btn3_click(interaction, button):
        await interaction.response.send_message("Вы нажали кнопку 3!")
    
    view.add_button(btn1, on_btn1_click)
    view.add_button(btn2, on_btn2_click)
    view.add_button(btn3, on_btn3_click)
    view.add_button(btn4)
    
    embed = Embed(title="Тест кнопок", description="Нажмите на кнопки ниже")
    await ctx.send(embed=embed, view=view)


@bot.command(name="select")
async def show_select(ctx):
    """Показать выпадающее меню"""
    view = SelectMenuView(timeout=60.0)
    
    # Создать меню
    menu = SelectMenu(
        custom_id="test_menu",
        placeholder="Выберите опцию",
        min_values=1,
        max_values=3,
        options=[
            {"label": "Опция 1", "value": "opt1", "description": "Первая опция"},
            {"label": "Опция 2", "value": "opt2", "description": "Вторая опция"},
            {"label": "Опция 3", "value": "opt3", "description": "Третья опция"},
        ]
    )
    
    async def on_select(interaction, menu, values):
        await interaction.response.send_message(f"Вы выбрали: {', '.join(values)}")
    
    view.add_select_menu(menu, on_select)
    
    embed = Embed(title="Тест меню", description="Выберите опции из меню")
    await ctx.send(embed=embed, view=view)


@bot.command(name="custom_view")
async def custom_view_example(ctx):
    """Пример кастомного View"""
    class MyView(View):
        def __init__(self):
            super().__init__(timeout=60.0)
            self.clicks = 0
        
        async def on_timeout(self):
            await ctx.send("⏰ Время вышло!")
        
        async def on_error(self, error, item, interaction):
            await ctx.send(f"❌ Ошибка: {error}")
    
    view = MyView()
    
    btn = Button(label=f"Кликов: {view.clicks}", style=1, custom_id="click_btn")
    
    async def on_click(interaction, button):
        view.clicks += 1
        button.label = f"Кликов: {view.clicks}"
        await interaction.response.edit_message(view=view)
    
    view.add_button(btn, on_click)
    
    await ctx.send("Нажмите на кнопку!", view=view)


@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")
    print("Попробуйте команды:")
    print("  !buttons - показать кнопки")
    print("  !select - показать выпадающее меню")
    print("  !custom_view - кастомный View")


async def main():
    async with client:
        await asyncio.sleep(3600 * 24)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

