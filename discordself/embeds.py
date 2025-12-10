"""Классы для создания Discord Embeds и компонентов"""

from typing import Optional, List, Dict, Any
from datetime import datetime


class Embed:
    """Класс для создания Discord Embed"""
    
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
        """Установить footer"""
        self.footer = {"text": text}
        if icon_url:
            self.footer["icon_url"] = icon_url
        return self
    
    def set_image(self, url: str):
        """Установить изображение"""
        self.image = {"url": url}
        return self
    
    def set_thumbnail(self, url: str):
        """Установить миниатюру"""
        self.thumbnail = {"url": url}
        return self
    
    def set_author(self, name: str, url: Optional[str] = None, icon_url: Optional[str] = None):
        """Установить автора"""
        self.author = {"name": name}
        if url:
            self.author["url"] = url
        if icon_url:
            self.author["icon_url"] = icon_url
        return self
    
    def add_field(self, name: str, value: str, inline: bool = False):
        """Добавить поле"""
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
        """Преобразовать в словарь для API"""
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
    """Класс для создания кнопки"""
    
    STYLE_PRIMARY = 1
    STYLE_SECONDARY = 2
    STYLE_SUCCESS = 3
    STYLE_DANGER = 4
    STYLE_LINK = 5
    
    def __init__(
        self,
        style: int,
        label: Optional[str] = None,
        emoji: Optional[Dict] = None,
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
        self.emoji = emoji
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled
    
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
    """Класс для создания выпадающего меню"""
    
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
    """Класс для создания строки действий (Action Row)"""
    
    def __init__(self, components: Optional[List] = None):
        self.type = 1  # Action Row component type
        self.components = components or []
    
    def add_button(self, button: Button):
        """Добавить кнопку"""
        if len(self.components) >= 5:
            raise ValueError("Action Row can have maximum 5 buttons")
        self.components.append(button)
        return self
    
    def add_select_menu(self, select_menu: SelectMenu):
        """Добавить выпадающее меню"""
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
    """Создать embed"""
    return Embed(**kwargs)


def create_button(style: int, **kwargs) -> Button:
    """Создать кнопку"""
    return Button(style, **kwargs)


def create_select_menu(custom_id: str, **kwargs) -> SelectMenu:
    """Создать выпадающее меню"""
    return SelectMenu(custom_id, **kwargs)


def create_action_row(**kwargs) -> ActionRow:
    """Создать строку действий"""
    return ActionRow(**kwargs)

