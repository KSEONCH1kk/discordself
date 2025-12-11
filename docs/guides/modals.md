# Modals - Модальные окна

Modals позволяют создавать формы для ввода данных пользователем.

## Создание Modal

### Базовый пример

```python
from discordself import InteractionType, InteractionResponseType
from discordself.enums import InteractionResponseType

@client.event("component_interaction")
async def on_button_click(interaction):
    if interaction.data.get("custom_id") == "open_modal":
        # Создать модальное окно
        components = [
            {
                "type": 1,  # ACTION_ROW
                "components": [
                    {
                        "type": 4,  # TEXT_INPUT
                        "custom_id": "name_input",
                        "label": "Ваше имя",
                        "style": 1,  # SHORT
                        "required": True,
                        "max_length": 100
                    }
                ]
            }
        ]
        
        await interaction.respond_modal(
            custom_id="user_form",
            title="Форма регистрации",
            components=components
        )
```

## Типы полей

### Короткий текст (SHORT)

```python
{
    "type": 4,  # TEXT_INPUT
    "custom_id": "short_input",
    "label": "Короткий текст",
    "style": 1,  # SHORT
    "required": True,
    "min_length": 1,
    "max_length": 100,
    "placeholder": "Введите текст..."
}
```

### Длинный текст (PARAGRAPH)

```python
{
    "type": 4,  # TEXT_INPUT
    "custom_id": "long_input",
    "label": "Длинный текст",
    "style": 2,  # PARAGRAPH
    "required": False,
    "min_length": 0,
    "max_length": 4000,
    "placeholder": "Введите длинный текст..."
}
```

## Обработка Modal

### Обработчик modal_submit

```python
@client.event("modal_submit")
async def on_modal_submit(interaction):
    if interaction.custom_id == "user_form":
        # Получить значения полей
        name = interaction.get_modal_value("name_input")
        
        await interaction.respond(
            content=f"Спасибо, {name}!"
        )
```

### Получение значений

```python
# Получить значение по custom_id
value = interaction.get_modal_value("field_custom_id")

# Или напрямую из компонентов
for row in interaction.components:
    for component in row.get("components", []):
        if component.get("custom_id") == "field_custom_id":
            value = component.get("value")
```

## Примеры

### Форма обратной связи

```python
@client.event("component_interaction")
async def on_feedback_button(interaction):
    if interaction.data.get("custom_id") == "feedback":
        components = [
            {
                "type": 1,
                "components": [
                    {
                        "type": 4,
                        "custom_id": "feedback_title",
                        "label": "Тема",
                        "style": 1,
                        "required": True,
                        "max_length": 100
                    }
                ]
            },
            {
                "type": 1,
                "components": [
                    {
                        "type": 4,
                        "custom_id": "feedback_text",
                        "label": "Сообщение",
                        "style": 2,
                        "required": True,
                        "max_length": 1000,
                        "placeholder": "Опишите вашу проблему или предложение..."
                    }
                ]
            }
        ]
        
        await interaction.respond_modal(
            custom_id="feedback_form",
            title="Обратная связь",
            components=components
        )

@client.event("modal_submit")
async def on_feedback_submit(interaction):
    if interaction.custom_id == "feedback_form":
        title = interaction.get_modal_value("feedback_title")
        text = interaction.get_modal_value("feedback_text")
        
        # Отправить в канал обратной связи
        await client.send_message(
            channel_id=FEEDBACK_CHANNEL_ID,
            content=f"**{title}**\n\n{text}\n\nОт: {interaction.user.mention}"
        )
        
        await interaction.respond(
            content="✅ Спасибо за обратную связь!",
            ephemeral=True
        )
```

### Форма настройки

```python
@client.event("component_interaction")
async def on_settings_button(interaction):
    if interaction.data.get("custom_id") == "settings":
        components = [
            {
                "type": 1,
                "components": [
                    {
                        "type": 4,
                        "custom_id": "prefix",
                        "label": "Префикс команд",
                        "style": 1,
                        "required": True,
                        "min_length": 1,
                        "max_length": 5,
                        "placeholder": "!"
                    }
                ]
            },
            {
                "type": 1,
                "components": [
                    {
                        "type": 4,
                        "custom_id": "language",
                        "label": "Язык",
                        "style": 1,
                        "required": True,
                        "placeholder": "ru или en"
                    }
                ]
            }
        ]
        
        await interaction.respond_modal(
            custom_id="settings_form",
            title="Настройки",
            components=components
        )

@client.event("modal_submit")
async def on_settings_submit(interaction):
    if interaction.custom_id == "settings_form":
        prefix = interaction.get_modal_value("prefix")
        language = interaction.get_modal_value("language")
        
        # Сохранить настройки
        # save_settings(interaction.user.id, prefix, language)
        
        await interaction.respond(
            content=f"✅ Настройки сохранены!\nПрефикс: {prefix}\nЯзык: {language}",
            ephemeral=True
        )
```

### Форма с валидацией

```python
@client.event("modal_submit")
async def on_form_submit(interaction):
    if interaction.custom_id == "registration":
        email = interaction.get_modal_value("email")
        age = interaction.get_modal_value("age")
        
        # Валидация
        if "@" not in email:
            await interaction.respond(
                content="❌ Неверный email!",
                ephemeral=True
            )
            return
        
        try:
            age_int = int(age)
            if age_int < 18:
                await interaction.respond(
                    content="❌ Вам должно быть 18+!",
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.respond(
                content="❌ Возраст должен быть числом!",
                ephemeral=True
            )
            return
        
        # Все проверки пройдены
        await interaction.respond(
            content="✅ Регистрация успешна!",
            ephemeral=True
        )
```

## Ограничения

- Максимум 5 полей в модальном окне
- Максимум 5 Action Rows
- Максимум 1 Text Input на Action Row
- Максимум 4000 символов для PARAGRAPH
- Максимум 100 символов для SHORT

## Best Practices

1. **Используйте понятные labels** для полей
2. **Добавляйте placeholder** для подсказок
3. **Валидируйте данные** перед обработкой
4. **Используйте required** для обязательных полей
5. **Ограничивайте длину** через min_length/max_length
6. **Используйте ephemeral=True** для приватных ответов

