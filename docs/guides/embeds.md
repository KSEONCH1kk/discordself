# Embeds и компоненты

DiscordSelf поддерживает создание красивых embed сообщений и интерактивных компонентов.

## Embeds

### Создание Embed

```python
from discordself import Embed

embed = Embed(
    title="Заголовок",
    description="Описание embed",
    color=0x00ff00  # Зеленый цвет
)
```

### Параметры Embed

```python
embed = Embed(
    title="Заголовок",
    description="Описание",
    url="https://example.com",  # URL для клика по заголовку
    color=0x00ff00,  # Цвет полоски
    timestamp="2024-01-01T00:00:00Z",  # Временная метка
    footer_text="Footer",
    footer_icon="https://example.com/icon.png",
    image_url="https://example.com/image.png",
    thumbnail_url="https://example.com/thumb.png",
    author_name="Author",
    author_url="https://example.com",
    author_icon="https://example.com/author.png"
)
```

### Добавление полей

```python
embed.add_field(name="Поле 1", value="Значение 1", inline=False)
embed.add_field(name="Поле 2", value="Значение 2", inline=True)
embed.add_field(name="Поле 3", value="Значение 3", inline=True)
```

### Отправка Embed

```python
await client.send_message(
    channel_id=123456789,
    embeds=[embed]
)
```

### Пример полного Embed

```python
from discordself import Embed

embed = Embed(
    title="Информация о пользователе",
    description=f"Информация о {user.mention}",
    color=0x3498db,
    timestamp=datetime.utcnow().isoformat()
)

embed.set_author(
    name=user.username,
    icon_url=user.avatar_url
)

embed.set_thumbnail(url=user.avatar_url)

embed.add_field(name="ID", value=user.id, inline=True)
embed.add_field(name="Создан", value=user.created_at, inline=True)
embed.add_field(name="Бот", value="Да" if user.bot else "Нет", inline=True)

embed.set_footer(text="DiscordSelf")

await ctx.send(embed=embed)
```

## Кнопки

### Создание кнопки

```python
from discordself import Button

button = Button(
    Button.STYLE_PRIMARY,  # Стиль кнопки
    label="Нажми меня",    # Текст
    custom_id="button_1"   # Уникальный ID
)
```

### Стили кнопок

```python
Button.STYLE_PRIMARY    # Синяя
Button.STYLE_SECONDARY  # Серая
Button.STYLE_SUCCESS    # Зеленая
Button.STYLE_DANGER     # Красная
Button.STYLE_LINK       # Ссылка (требует url)
```

### Кнопка-ссылка

```python
button = Button(
    Button.STYLE_LINK,
    label="Открыть сайт",
    url="https://example.com"
)
```

### Кнопка с эмодзи

```python
button = Button(
    Button.STYLE_PRIMARY,
    label="Кнопка",
    emoji="👍",
    custom_id="button_1"
)
```

### Отключенная кнопка

```python
button = Button(
    Button.STYLE_PRIMARY,
    label="Кнопка",
    custom_id="button_1",
    disabled=True
)
```

### ActionRow

Кнопки должны быть в ActionRow (максимум 5 кнопок в ряду):

```python
from discordself import ActionRow

row = ActionRow()
row.add_button(button1)
row.add_button(button2)
row.add_button(button3)

await client.send_message(
    channel_id=123456789,
    content="Выберите действие:",
    components=[row]
)
```

### Обработка нажатий кнопок

```python
@client.event("component_interaction")
async def on_button_click(interaction):
    if interaction.data.get("custom_id") == "button_1":
        await interaction.respond(content="Кнопка нажата!")
```

## Выпадающие меню (Select Menu)

### Создание меню

```python
from discordself import SelectMenu

menu = SelectMenu(
    custom_id="menu_1",
    placeholder="Выберите опцию",
    min_values=1,
    max_values=3
)

menu.add_option(
    label="Опция 1",
    value="option_1",
    description="Описание опции 1",
    emoji="1️⃣"
)

menu.add_option(
    label="Опция 2",
    value="option_2",
    description="Описание опции 2",
    emoji="2️⃣"
)
```

### Отправка меню

```python
row = ActionRow()
row.add_select_menu(menu)

await client.send_message(
    channel_id=123456789,
    content="Выберите опции:",
    components=[row]
)
```

### Обработка выбора

```python
@client.event("component_interaction")
async def on_select(interaction):
    if interaction.data.get("custom_id") == "menu_1":
        values = interaction.data.get("values", [])
        await interaction.respond(
            content=f"Выбрано: {', '.join(values)}"
        )
```

## Views

Views позволяют создавать интерактивные интерфейсы с кнопками и меню.

### Создание View

```python
from discordself.views import View, ButtonView

class MyView(ButtonView):
    def __init__(self):
        super().__init__(timeout=60.0)
        
        # Добавить кнопки
        self.add_button(
            Button.STYLE_PRIMARY,
            "Кнопка 1",
            "btn1",
            callback=self.on_button1
        )
    
    async def on_button1(self, interaction, button):
        await interaction.respond(content="Кнопка 1 нажата!")
```

### Использование View

```python
view = MyView()
await ctx.send("Выберите действие:", view=view)
```

## Примеры

### Меню выбора

```python
from discordself import SelectMenu, ActionRow

menu = SelectMenu(
    custom_id="color_menu",
    placeholder="Выберите цвет"
)

colors = ["Красный", "Зеленый", "Синий", "Желтый"]
for color in colors:
    menu.add_option(
        label=color,
        value=color.lower(),
        emoji="🎨"
    )

row = ActionRow()
row.add_select_menu(menu)

await ctx.send("Выберите цвет:", components=[row])
```

### Интерактивная форма

```python
from discordself import Button, ActionRow

# Кнопки подтверждения
confirm_btn = Button(
    Button.STYLE_SUCCESS,
    "Подтвердить",
    "confirm",
    emoji="✅"
)

cancel_btn = Button(
    Button.STYLE_DANGER,
    "Отменить",
    "cancel",
    emoji="❌"
)

row = ActionRow()
row.add_button(confirm_btn)
row.add_button(cancel_btn)

await ctx.send("Подтвердите действие:", components=[row])
```

### Обновление сообщения с кнопками

```python
@client.event("component_interaction")
async def on_button_click(interaction):
    if interaction.data.get("custom_id") == "update":
        # Создать новые кнопки
        new_button = Button(
            Button.STYLE_SECONDARY,
            "Обновлено!",
            "updated",
            disabled=True
        )
        
        row = ActionRow()
        row.add_button(new_button)
        
        # Обновить сообщение
        await interaction.respond(
            content="Сообщение обновлено!",
            components=[row]
        )
```

## Best Practices

1. **Используйте уникальные custom_id** для каждой кнопки/меню
2. **Ограничивайте количество кнопок** (максимум 5 в ряду, 5 рядов)
3. **Обрабатывайте timeout** для Views
4. **Проверяйте автора** при обработке interactions
5. **Используйте эмодзи** для лучшего UX

