# Views - Интерактивные компоненты

Views позволяют создавать интерактивные интерфейсы с кнопками и выпадающими меню.

## Базовое использование

### ButtonView

```python
from discordself.views import ButtonView
from discordself.embeds import Button

view = ButtonView(timeout=60.0)

# Добавить кнопку
btn = Button(label="Нажми меня", style=1, custom_id="btn1")

async def on_click(interaction, button):
    await interaction.respond(content="Кнопка нажата!")

view.add_button(btn, on_click)

await ctx.send("Выберите действие:", view=view)
```

### SelectMenuView

```python
from discordself.views import SelectMenuView
from discordself.embeds import SelectMenu

view = SelectMenuView(timeout=60.0)

menu = SelectMenu(
    custom_id="menu1",
    placeholder="Выберите опцию",
    min_values=1,
    max_values=3
)

menu.add_option(label="Опция 1", value="opt1", emoji="1️⃣")
menu.add_option(label="Опция 2", value="opt2", emoji="2️⃣")

async def on_select(interaction, menu, values):
    await interaction.respond(content=f"Выбрано: {', '.join(values)}")

view.add_select_menu(menu, on_select)

await ctx.send("Выберите опции:", view=view)
```

## Кастомные Views

### Создание кастомного View

```python
from discordself.views import View

class MyView(View):
    def __init__(self):
        super().__init__(timeout=60.0)
        self.clicks = 0
    
    async def on_timeout(self):
        await self.message.channel.send("⏰ Время вышло!")
    
    async def on_error(self, error, item, interaction):
        await interaction.respond(
            content=f"❌ Ошибка: {error}",
            ephemeral=True
        )

# Использование
view = MyView()
btn = Button(label="Клик", style=1, custom_id="click")

async def on_click(interaction, button):
    view.clicks += 1
    button.label = f"Кликов: {view.clicks}"
    await interaction.respond(
        content=f"Кликов: {view.clicks}",
        components=[view.to_dict()]
    )

view.add_button(btn, on_click)
await ctx.send("Нажмите кнопку!", view=view)
```

## Примеры

### Система голосования

```python
class VoteView(ButtonView):
    def __init__(self, question):
        super().__init__(timeout=300.0)
        self.question = question
        self.votes = {"yes": 0, "no": 0}
        self.voters = set()
    
    async def on_yes(self, interaction, button):
        if interaction.user.id in self.voters:
            await interaction.respond(
                content="❌ Вы уже проголосовали!",
                ephemeral=True
            )
            return
        
        self.votes["yes"] += 1
        self.voters.add(interaction.user.id)
        await interaction.respond(
            content="✅ Ваш голос учтен!",
            ephemeral=True
        )
        await self.update_message()
    
    async def on_no(self, interaction, button):
        if interaction.user.id in self.voters:
            await interaction.respond(
                content="❌ Вы уже проголосовали!",
                ephemeral=True
            )
            return
        
        self.votes["no"] += 1
        self.voters.add(interaction.user.id)
        await interaction.respond(
            content="✅ Ваш голос учтен!",
            ephemeral=True
        )
        await self.update_message()
    
    async def update_message(self):
        embed = Embed(
            title=self.question,
            color=0x3498db
        )
        embed.add_field(name="✅ Да", value=self.votes["yes"])
        embed.add_field(name="❌ Нет", value=self.votes["no"])
        embed.set_footer(text=f"Проголосовало: {len(self.voters)}")
        
        await self.message.edit(embed=embed, view=self)

# Использование
view = VoteView("Нравится ли вам этот бот?")
yes_btn = Button(label="Да", style=3, custom_id="yes", emoji="✅")
no_btn = Button(label="Нет", style=4, custom_id="no", emoji="❌")

view.add_button(yes_btn, view.on_yes)
view.add_button(no_btn, view.on_no)

message = await ctx.send("Голосование:", view=view)
view.message = message
```

### Пагинация

```python
class PaginatorView(ButtonView):
    def __init__(self, pages):
        super().__init__(timeout=300.0)
        self.pages = pages
        self.current_page = 0
    
    async def on_previous(self, interaction, button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)
    
    async def on_next(self, interaction, button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.update_message(interaction)
    
    async def update_message(self, interaction):
        embed = self.pages[self.current_page]
        embed.set_footer(text=f"Страница {self.current_page + 1}/{len(self.pages)}")
        
        prev_btn = Button(
            label="◀",
            style=2,
            custom_id="prev",
            disabled=self.current_page == 0
        )
        next_btn = Button(
            label="▶",
            style=2,
            custom_id="next",
            disabled=self.current_page == len(self.pages) - 1
        )
        
        self.clear_items()
        self.add_button(prev_btn, self.on_previous)
        self.add_button(next_btn, self.on_next)
        
        await interaction.respond(
            embed=embed,
            view=self
        )

# Использование
pages = [Embed(title=f"Страница {i}") for i in range(5)]
view = PaginatorView(pages)
# ... добавить кнопки и отправить
```

## Best Practices

1. **Используйте timeout** для автоматической очистки
2. **Обрабатывайте ошибки** в on_error
3. **Обновляйте сообщения** для интерактивности
4. **Проверяйте автора** для безопасности
5. **Ограничивайте количество компонентов** (максимум 5 в ряду)

