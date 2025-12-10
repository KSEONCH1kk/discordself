"""Проверки (checks) для команд"""

from typing import Callable, List, Optional
from .commands import Context
from .exceptions import (
    CheckFailure,
    MissingPermissions,
    BotMissingPermissions,
    NoPrivateMessage,
    PrivateMessageOnly
)
from .models import Member, User


def check(predicate: Callable) -> Callable:
    """Декоратор для создания check функции"""
    def decorator(func: Callable) -> Callable:
        func.__check__ = predicate
        return func
    return decorator


def has_permissions(*permissions: str):
    """Проверка наличия прав у автора команды"""
    def predicate(ctx: Context) -> bool:
        if not ctx.guild or not isinstance(ctx.author, Member):
            raise NoPrivateMessage()
        
        # Получить permissions автора
        # Упрощенная версия - нужно реализовать получение permissions
        # В реальной версии нужно получить permissions из ролей
        return True  # Заглушка
    
    return predicate


def bot_has_permissions(*permissions: str):
    """Проверка наличия прав у бота"""
    def predicate(ctx: Context) -> bool:
        if not ctx.guild or not ctx.me:
            raise NoPrivateMessage()
        
        # Получить permissions бота
        # Упрощенная версия
        return True  # Заглушка
    
    return predicate


def has_role(item: str):
    """Проверка наличия роли у автора"""
    def predicate(ctx: Context) -> bool:
        if not ctx.guild or not isinstance(ctx.author, Member):
            raise NoPrivateMessage()
        
        # Проверка роли
        # Упрощенная версия
        return True  # Заглушка
    
    return predicate


def has_any_role(*items: str):
    """Проверка наличия хотя бы одной роли"""
    def predicate(ctx: Context) -> bool:
        if not ctx.guild or not isinstance(ctx.author, Member):
            raise NoPrivateMessage()
        
        # Проверка ролей
        return True  # Заглушка
    
    return predicate


def is_owner():
    """Проверка, что автор - владелец бота"""
    def predicate(ctx: Context) -> bool:
        if not ctx.bot or not ctx.bot.client:
            return False
        # Проверка владельца
        # Можно добавить owner_ids в Bot
        return True  # Заглушка
    
    return predicate


def is_nsfw():
    """Проверка, что канал NSFW"""
    def predicate(ctx: Context) -> bool:
        if not ctx.channel:
            return False
        return getattr(ctx.channel, 'nsfw', False)
    
    return predicate


def guild_only():
    """Проверка, что команда выполняется на сервере"""
    def predicate(ctx: Context) -> bool:
        if not ctx.guild:
            raise NoPrivateMessage()
        return True
    
    return predicate


def dm_only():
    """Проверка, что команда выполняется в личных сообщениях"""
    def predicate(ctx: Context) -> bool:
        if ctx.guild:
            raise PrivateMessageOnly()
        return True
    
    return predicate


def cooldown(rate: int, per: float, type: int = 1):
    """Система cooldown для команд"""
    # type: 1 = per user, 2 = per guild, 3 = per channel, 4 = global
    def decorator(func: Callable) -> Callable:
        func.__cooldown__ = (rate, per, type)
        return func
    return decorator

