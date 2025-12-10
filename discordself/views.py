"""Views (UI Components) для Discord Selfbot"""

import asyncio
from typing import Optional, List, Dict, Any, Callable
from .embeds import Embed, Button, SelectMenu, ActionRow


class View:
    """Базовый класс для View (UI компонентов)"""
    
    def __init__(self, timeout: Optional[float] = 180.0):
        self.timeout = timeout
        self.children: List[Any] = []
        self._message = None
        self._interaction_handlers: Dict[str, Callable] = {}
        self._stopped = False
    
    def add_item(self, item: Any):
        """Добавить компонент в View"""
        if len(self.children) >= 5:
            raise ValueError("View can have at most 5 components")
        self.children.append(item)
        return item
    
    def remove_item(self, item: Any):
        """Удалить компонент из View"""
        if item in self.children:
            self.children.remove(item)
    
    def clear_items(self):
        """Очистить все компоненты"""
        self.children.clear()
    
    async def on_timeout(self):
        """Вызывается при истечении времени ожидания"""
        pass
    
    async def on_error(self, error: Exception, item: Any, interaction: Any):
        """Обработчик ошибок"""
        import traceback
        traceback.print_exc()
    
    def stop(self):
        """Остановить View"""
        self._stopped = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать View в словарь для Discord API"""
        components = []
        for child in self.children:
            if hasattr(child, 'to_dict'):
                components.append(child.to_dict())
        
        return {
            "type": 1,  # ACTION_ROW
            "components": components
        } if components else {}


class ButtonView(View):
    """View с кнопками"""
    
    def __init__(self, timeout: Optional[float] = 180.0):
        super().__init__(timeout)
        self.buttons: Dict[str, Button] = {}
    
    def add_button(self, button: Button, callback: Optional[Callable] = None):
        """Добавить кнопку"""
        if len(self.children) >= 5:
            raise ValueError("View can have at most 5 buttons")
        
        self.add_item(button)
        if callback:
            self._interaction_handlers[button.custom_id] = callback
        return button
    
    async def on_button_click(self, interaction: Any, button: Button):
        """Обработчик клика по кнопке"""
        handler = self._interaction_handlers.get(button.custom_id)
        if handler:
            if asyncio.iscoroutinefunction(handler):
                await handler(interaction, button)
            else:
                handler(interaction, button)


class SelectMenuView(View):
    """View с выпадающим меню"""
    
    def __init__(self, timeout: Optional[float] = 180.0):
        super().__init__(timeout)
        self.menus: Dict[str, SelectMenu] = {}
    
    def add_select_menu(self, menu: SelectMenu, callback: Optional[Callable] = None):
        """Добавить выпадающее меню"""
        if len(self.children) >= 5:
            raise ValueError("View can have at most 5 select menus")
        
        self.add_item(menu)
        if callback:
            self._interaction_handlers[menu.custom_id] = callback
        return menu
    
    async def on_select(self, interaction: Any, menu: SelectMenu, values: List[str]):
        """Обработчик выбора в меню"""
        handler = self._interaction_handlers.get(menu.custom_id)
        if handler:
            if asyncio.iscoroutinefunction(handler):
                await handler(interaction, menu, values)
            else:
                handler(interaction, menu, values)


def button(label: str, style: int = 1, custom_id: Optional[str] = None, 
           emoji: Optional[str] = None, disabled: bool = False, url: Optional[str] = None):
    """Декоратор для создания кнопки"""
    def decorator(func: Callable) -> Button:
        btn = Button(
            label=label,
            style=style,
            custom_id=custom_id or f"btn_{func.__name__}",
            emoji=emoji,
            disabled=disabled,
            url=url
        )
        btn.callback = func
        return btn
    return decorator

