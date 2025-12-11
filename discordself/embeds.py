"""Классы для создания Discord Embeds и компонентов.

Этот модуль предоставляет классы для создания красивых embed сообщений
и интерактивных компонентов (кнопки, выпадающие меню) для Discord.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime


class Embed:
    """Класс для создания Discord Embed сообщений.
    
    Embed - это форматированные сообщения с заголовком, описанием,
    полями, изображениями и другими элементами.
    
    Args:
        title: Заголовок embed
        description: Описание embed
        color: Цвет полоски embed (hex число, например 0x00ff00)
        url: URL для клика по заголовку
        timestamp: Временная метка
        footer: Footer embed (dict с text и icon_url)
        image: Изображение embed (dict с url)
        thumbnail: Миниатюра embed (dict с url)
        video: Видео embed (dict с url)
        provider: Провайдер embed (dict)
        author: Автор embed (dict с name, url, icon_url)
        fields: Список полей embed (список dict)
    
    Example:
        ```python
        embed = Embed(
            title="Заголовок",
            description="Описание",
            color=0x00ff00
        )
        embed.add_field(name="Поле", value="Значение")
        ```
    """
    
    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[int] = None,
        url: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        footer: Optional[Dict] = None,
        image: Optional[Dict] = None,
        thumbnail: Optional[Dict] = None,
        video: Optional[Dict] = None,
        provider: Optional[Dict] = None,
        author: Optional[Dict] = None,
        fields: Optional[List[Dict]] = None
    ):
        self.title = title
        self.description = description
        self.color = color
        self.url = url
        self.timestamp = timestamp.isoformat() if timestamp else None
        self.footer = footer
        self.image = image
        self.thumbnail = thumbnail
        self.video = video
        self.provider = provider
        self.author = author
        self.fields = fields or []
    
    def set_footer(self, text: str, icon_url: Optional[str] = None):
        """Установить footer для embed.
        
        Args:
            text: Текст footer
            icon_url: URL иконки footer (опционально)
        
        Returns:
            Embed: self для цепочки вызовов
        """
        self.footer = {"text": text}
        if icon_url:
            self.footer["icon_url"] = icon_url
        return self
    
    def set_image(self, url: str):
        """Установить изображение для embed.
        
        Args:
            url: URL изображения
        
        Returns:
            Embed: self для цепочки вызовов
        """
        self.image = {"url": url}
        return self
    
    def set_thumbnail(self, url: str):
        """Установить миниатюру для embed.
        
        Args:
            url: URL миниатюры
        
        Returns:
            Embed: self для цепочки вызовов
        """
        self.thumbnail = {"url": url}
        return self
    
    def set_author(self, name: str, url: Optional[str] = None, icon_url: Optional[str] = None):
        """Установить автора для embed.
        
        Args:
            name: Имя автора
            url: URL для клика по имени (опционально)
            icon_url: URL иконки автора (опционально)
        
        Returns:
            Embed: self для цепочки вызовов
        """
        self.author = {"name": name}
        if url:
            self.author["url"] = url
        if icon_url:
            self.author["icon_url"] = icon_url
        return self
    
    def add_field(self, name: str, value: str, inline: bool = False):
        """Добавить поле в embed.
        
        Args:
            name: Название поля
            value: Значение поля
            inline: Отображать ли поле в одной строке (по умолчанию: False)
        
        Returns:
            Embed: self для цепочки вызовов
        """
        self.fields.append({
            "name": name,
            "value": value,
            "inline": inline
        })
        return self
    
    def insert_field_at(self, index: int, name: str, value: str, inline: bool = False):
        """Вставить поле по индексу"""
        self.fields.insert(index, {
            "name": name,
            "value": value,
            "inline": inline
        })
        return self
    
    def remove_field(self, index: int):
        """Удалить поле по индексу"""
        self.fields.pop(index)
        return self
    
    def clear_fields(self):
        """Очистить все поля"""
        self.fields.clear()
        return self
    
    def to_dict(self) -> Dict:
        """Преобразовать embed в словарь для Discord API.
        
        Returns:
            Dict: Словарь с данными embed
        """
        data = {}
        if self.title:
            data["title"] = self.title
        if self.description:
            data["description"] = self.description
        if self.color is not None:
            data["color"] = self.color
        if self.url:
            data["url"] = self.url
        if self.timestamp:
            data["timestamp"] = self.timestamp
        if self.footer:
            data["footer"] = self.footer
        if self.image:
            data["image"] = self.image
        if self.thumbnail:
            data["thumbnail"] = self.thumbnail
        if self.video:
            data["video"] = self.video
        if self.provider:
            data["provider"] = self.provider
        if self.author:
            data["author"] = self.author
        if self.fields:
            data["fields"] = self.fields
        return data


class Button:
    """Класс для создания интерактивной кнопки Discord.
    
    Кнопки позволяют пользователям взаимодействовать с сообщениями.
    Поддерживаются различные стили и эмодзи.
    
    Attributes:
        STYLE_PRIMARY: Синий стиль кнопки (1)
        STYLE_SECONDARY: Серый стиль кнопки (2)
        STYLE_SUCCESS: Зеленый стиль кнопки (3)
        STYLE_DANGER: Красный стиль кнопки (4)
        STYLE_LINK: Стиль ссылки (5)
    
    Args:
        style: Стиль кнопки (используйте константы STYLE_*)
        label: Текст кнопки
        emoji: Эмодзи для кнопки (строка или dict)
        custom_id: Уникальный ID кнопки (обязателен для не-link кнопок)
        url: URL для link кнопок (обязателен для STYLE_LINK)
        disabled: Отключена ли кнопка (по умолчанию: False)
    
    Raises:
        ValueError: Если link кнопка без url или не-link кнопка без custom_id
    
    Example:
        ```python
        button = Button(
            Button.STYLE_PRIMARY,
            label="Нажми меня",
            emoji="👍",
            custom_id="btn1"
        )
        ```
    """
    
    STYLE_PRIMARY = 1
    STYLE_SECONDARY = 2
    STYLE_SUCCESS = 3
    STYLE_DANGER = 4
    STYLE_LINK = 5
    
    def __init__(
        self,
        style: int,
        label: Optional[str] = None,
        emoji: Optional[Any] = None,
        custom_id: Optional[str] = None,
        url: Optional[str] = None,
        disabled: bool = False
    ):
        if style == self.STYLE_LINK and not url:
            raise ValueError("Link buttons must have a url")
        if style != self.STYLE_LINK and not custom_id:
            raise ValueError("Non-link buttons must have a custom_id")
        
        self.style = style
        self.label = label
        self.emoji = self._parse_emoji(emoji) if emoji else None
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled
    
    def _parse_emoji(self, emoji: Any) -> Optional[Dict]:
        """Преобразовать эмодзи в формат Discord API.
        
        Поддерживает Unicode эмодзи (строка), кастомные эмодзи (<:name:id>)
        и уже готовые объекты (dict).
        
        Args:
            emoji: Эмодзи в любом формате
        
        Returns:
            Optional[Dict]: Объект эмодзи для Discord API или None
        """
        if isinstance(emoji, dict):
            if "name" in emoji or "id" in emoji:
                return emoji
            return None
        elif isinstance(emoji, str):
            emoji = emoji.strip()
            if not emoji:
                return None
            
            if emoji.startswith("<") and emoji.endswith(">"):
                parts = emoji.strip("<>").split(":")
                if len(parts) >= 3:
                    animated = parts[0] == "a"
                    emoji_name = parts[1]
                    emoji_id = parts[2]
                    result = {
                        "name": emoji_name,
                        "animated": animated
                    }
                    if emoji_id.isdigit():
                        result["id"] = int(emoji_id)
                    return result
                elif len(parts) == 2:
                    return {
                        "name": parts[1]
                    }
            else:
                return {"name": emoji}
        return None
    
    def to_dict(self) -> Dict:
        """Преобразовать в словарь"""
        data = {
            "type": 2,  # Button component type
            "style": self.style,
            "disabled": self.disabled
        }
        if self.label:
            data["label"] = self.label
        if self.emoji:
            data["emoji"] = self.emoji
        if self.custom_id:
            data["custom_id"] = self.custom_id
        if self.url:
            data["url"] = self.url
        return data


class SelectMenu:
    """Класс для создания выпадающего меню Discord.
    
    Select Menu позволяет пользователям выбирать одну или несколько опций
    из выпадающего списка.
    
    Args:
        custom_id: Уникальный ID меню
        options: Список опций (список dict с label, value и опционально description, emoji)
        placeholder: Текст placeholder (по умолчанию: None)
        min_values: Минимальное количество выбранных опций (по умолчанию: None)
        max_values: Максимальное количество выбранных опций (по умолчанию: None)
        disabled: Отключено ли меню (по умолчанию: False)
    
    Example:
        ```python
        menu = SelectMenu(
            custom_id="menu1",
            options=[
                {"label": "Опция 1", "value": "opt1"},
                {"label": "Опция 2", "value": "opt2"}
            ],
            placeholder="Выберите опцию"
        )
        ```
    """
    
    def __init__(
        self,
        custom_id: str,
        options: List[Dict],
        placeholder: Optional[str] = None,
        min_values: Optional[int] = None,
        max_values: Optional[int] = None,
        disabled: bool = False
    ):
        self.type = 3  # Select menu component type
        self.custom_id = custom_id
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled
    
    def add_option(
        self,
        label: str,
        value: str,
        description: Optional[str] = None,
        emoji: Optional[Dict] = None,
        default: bool = False
    ):
        """Добавить опцию"""
        option = {
            "label": label,
            "value": value,
            "default": default
        }
        if description:
            option["description"] = description
        if emoji:
            option["emoji"] = emoji
        self.options.append(option)
        return self
    
    def to_dict(self) -> Dict:
        """Преобразовать в словарь"""
        data = {
            "type": self.type,
            "custom_id": self.custom_id,
            "options": self.options,
            "disabled": self.disabled
        }
        if self.placeholder:
            data["placeholder"] = self.placeholder
        if self.min_values is not None:
            data["min_values"] = self.min_values
        if self.max_values is not None:
            data["max_values"] = self.max_values
        return data


class ActionRow:
    """Класс для создания строки действий (Action Row).
    
    Action Row содержит компоненты (кнопки или меню).
    Максимум 5 кнопок в одном ряду, 1 меню в ряду.
    
    Args:
        components: Список компонентов (по умолчанию: пустой список)
    
    Example:
        ```python
        row = ActionRow()
        row.add_button(button1)
        row.add_button(button2)
        ```
    """
    
    def __init__(self, components: Optional[List] = None):
        self.type = 1  # Action Row component type
        self.components = components or []
    
    def add_button(self, button: Button):
        """Добавить кнопку в ряд.
        
        Args:
            button: Объект Button для добавления
        
        Returns:
            ActionRow: self для цепочки вызовов
        
        Raises:
            ValueError: Если в ряду уже 5 кнопок
        """
        if len(self.components) >= 5:
            raise ValueError("Action Row can have maximum 5 buttons")
        self.components.append(button)
        return self
    
    def add_select_menu(self, select_menu: SelectMenu):
        """Добавить выпадающее меню в ряд.
        
        Args:
            select_menu: Объект SelectMenu для добавления
        
        Returns:
            ActionRow: self для цепочки вызовов
        
        Raises:
            ValueError: Если в ряду уже есть компоненты
        """
        if self.components:
            raise ValueError("Action Row can only have one select menu")
        self.components.append(select_menu)
        return self
    
    def to_dict(self) -> Dict:
        """Преобразовать в словарь"""
        return {
            "type": self.type,
            "components": [comp.to_dict() if hasattr(comp, 'to_dict') else comp for comp in self.components]
        }


def create_embed(**kwargs) -> Embed:
    """Создать embed сообщение.
    
    Удобная функция для создания Embed с передачей параметров через kwargs.
    
    Args:
        **kwargs: Параметры для Embed (title, description, color и т.д.)
    
    Returns:
        Embed: Созданный объект Embed
    
    Example:
        ```python
        embed = create_embed(title="Заголовок", description="Описание")
        ```
    """
    return Embed(**kwargs)


def create_button(style: int, **kwargs) -> Button:
    """Создать кнопку.
    
    Удобная функция для создания Button с передачей параметров через kwargs.
    
    Args:
        style: Стиль кнопки (Button.STYLE_*)
        **kwargs: Параметры для Button (label, emoji, custom_id и т.д.)
    
    Returns:
        Button: Созданный объект Button
    
    Example:
        ```python
        button = create_button(Button.STYLE_PRIMARY, label="Кнопка", custom_id="btn1")
        ```
    """
    return Button(style, **kwargs)


def create_select_menu(custom_id: str, **kwargs) -> SelectMenu:
    """Создать выпадающее меню.
    
    Удобная функция для создания SelectMenu с передачей параметров через kwargs.
    
    Args:
        custom_id: Уникальный ID меню
        **kwargs: Параметры для SelectMenu (options, placeholder и т.д.)
    
    Returns:
        SelectMenu: Созданный объект SelectMenu
    
    Example:
        ```python
        menu = create_select_menu("menu1", options=[...], placeholder="Выберите")
        ```
    """
    return SelectMenu(custom_id, **kwargs)


def create_action_row(**kwargs) -> ActionRow:
    """Создать строку действий.
    
    Удобная функция для создания ActionRow.
    
    Args:
        **kwargs: Параметры для ActionRow (components)
    
    Returns:
        ActionRow: Созданный объект ActionRow
    
    Example:
        ```python
        row = create_action_row()
        ```
    """
    return ActionRow(**kwargs)

