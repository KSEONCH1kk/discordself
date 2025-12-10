"""Система Cogs для модульной организации команд"""

import inspect
from typing import Optional, Dict, List, Callable, Any
from .commands import Command, CommandGroup, Bot
from .client import Client


class Cog:
    """Базовый класс для Cog"""
    
    def __init__(self, bot: Optional[Bot] = None):
        self.bot = bot
        self._commands: Dict[str, Command] = {}
        self._listeners: Dict[str, List[Callable]] = {}
    
    def _load_commands(self):
        """Загрузить команды из Cog"""
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, '__command__'):
                command = method.__command__
                self._commands[command.name] = command
                if self.bot:
                    self.bot.add_command(command)
    
    def _load_listeners(self):
        """Загрузить listeners из Cog"""
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, '__listener__'):
                event_name = method.__listener__
                if event_name not in self._listeners:
                    self._listeners[event_name] = []
                self._listeners[event_name].append(method)
                if self.bot and self.bot.client:
                    self.bot.client.event(event_name)(method)
    
    def cog_load(self):
        """Вызывается при загрузке Cog"""
        pass
    
    def cog_unload(self):
        """Вызывается при выгрузке Cog"""
        pass
    
    def cog_check(self, ctx) -> bool:
        """Проверка для всех команд в Cog"""
        return True
    
    def cog_command_error(self, ctx, error: Exception):
        """Обработка ошибок команд в Cog"""
        pass
    
    def cog_before_invoke(self, ctx):
        """Вызывается перед выполнением команды"""
        pass
    
    def cog_after_invoke(self, ctx):
        """Вызывается после выполнения команды"""
        pass


def command(name: Optional[str] = None, **kwargs):
    """Декоратор для создания команды в Cog"""
    def decorator(func: Callable):
        cmd = Command(func, name=name, **kwargs)
        func.__command__ = cmd
        return func
    return decorator


def group(name: Optional[str] = None, **kwargs):
    """Декоратор для создания группы команд в Cog"""
    def decorator(func: Callable):
        # Это будет обработано в Bot.group
        func.__group__ = True
        return func
    return decorator


def listener(name: Optional[str] = None):
    """Декоратор для создания listener в Cog"""
    def decorator(func: Callable):
        event_name = name or func.__name__
        func.__listener__ = event_name
        return func
    return decorator


class CogManager:
    """Менеджер для управления Cogs"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.cogs: Dict[str, Cog] = {}
    
    def add_cog(self, cog: Cog, *, override: bool = False):
        """Добавить Cog"""
        if not isinstance(cog, Cog):
            raise TypeError("Cog must be an instance of Cog")
        
        cog_name = cog.__class__.__name__
        
        if cog_name in self.cogs and not override:
            raise ValueError(f"Cog '{cog_name}' is already loaded")
        
        # Установить bot
        cog.bot = self.bot
        
        # Загрузить команды и listeners
        cog._load_commands()
        cog._load_listeners()
        
        # Вызвать cog_load
        cog.cog_load()
        
        self.cogs[cog_name] = cog
    
    def remove_cog(self, name: str):
        """Удалить Cog"""
        cog = self.cogs.pop(name, None)
        if cog:
            # Удалить команды
            for command_name, command in cog._commands.items():
                self.bot.commands.pop(command_name, None)
                for alias in command.aliases:
                    self.bot.aliases.pop(alias, None)
            
            # Удалить listeners
            for event_name, listeners in cog._listeners.items():
                if self.bot.client and event_name in self.bot.client.event_handlers:
                    for listener in listeners:
                        if listener in self.bot.client.event_handlers[event_name]:
                            self.bot.client.event_handlers[event_name].remove(listener)
            
            # Вызвать cog_unload
            cog.cog_unload()
            
            return cog
        return None
    
    def get_cog(self, name: str) -> Optional[Cog]:
        """Получить Cog по имени"""
        return self.cogs.get(name)
    
    def reload_cog(self, name: str):
        """Перезагрузить Cog"""
        cog = self.remove_cog(name)
        if cog:
            # Пересоздать экземпляр
            cog_class = cog.__class__
            new_cog = cog_class()
            self.add_cog(new_cog, override=True)
            return new_cog
        return None

