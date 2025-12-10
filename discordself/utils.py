"""Утилиты для DiscordSelf библиотеки"""

import re
from typing import Optional, Tuple
from datetime import datetime, timezone


def parse_emoji(emoji: str) -> Tuple[Optional[str], Optional[int], bool]:
    """
    Парсить эмодзи из строки
    
    Примеры:
        parse_emoji("<:name:123456789>") -> ("name", 123456789, False)
        parse_emoji("<a:name:123456789>") -> ("name", 123456789, True)
        parse_emoji("👍") -> (None, None, False)
    """
    match = re.match(r'<(a?):(\w+):(\d+)>', emoji)
    if match:
        animated = bool(match.group(1))
        name = match.group(2)
        emoji_id = int(match.group(3))
        return name, emoji_id, animated
    return None, None, False


def format_emoji(name: str, emoji_id: int, animated: bool = False) -> str:
    """Форматировать эмодзи в строку"""
    prefix = "a" if animated else ""
    return f"<{prefix}:{name}:{emoji_id}>"


def snowflake_time(snowflake: int) -> datetime:
    """Получить время создания снежинки (Discord ID)"""
    timestamp = ((snowflake >> 22) + 1420070400000) / 1000
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def parse_timestamp(timestamp: str) -> datetime:
    """Парсить ISO timestamp в datetime"""
    try:
        # Discord использует ISO 8601 формат
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except:
        return datetime.now(timezone.utc)


def escape_markdown(text: str) -> str:
    """Экранировать markdown символы"""
    return re.sub(r'([*_`~|\\])', r'\\\1', text)


def clean_content(content: str, guild=None) -> str:
    """Очистить контент от упоминаний и т.д."""
    # Упрощенная версия, можно расширить
    return content


def find_channel(channels, **kwargs):
    """Найти канал по параметрам"""
    for channel in channels:
        match = True
        for key, value in kwargs.items():
            if getattr(channel, key, None) != value:
                match = False
                break
        if match:
            return channel
    return None


def find_role(roles, **kwargs):
    """Найти роль по параметрам"""
    for role in roles:
        match = True
        for key, value in kwargs.items():
            if getattr(role, key, None) != value:
                match = False
                break
        if match:
            return role
    return None


def calculate_permissions(member, guild):
    """Вычислить права участника"""
    # Упрощенная версия, можно расширить
    if guild.owner_id == member.user.id:
        return 0xFFFFFFFF  # Все права
    
    # Базовая роль @everyone
    permissions = 0
    
    # Добавить права из ролей
    for role_id in member.roles:
        role = find_role(guild.roles, id=role_id)
        if role:
            permissions |= int(role.permissions)
    
    return permissions


def has_permission(member, guild, permission: int) -> bool:
    """Проверить наличие права у участника"""
    perms = calculate_permissions(member, guild)
    return (perms & permission) == permission

