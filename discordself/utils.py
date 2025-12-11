"""Утилиты для DiscordSelf библиотеки.

Этот модуль содержит вспомогательные функции для работы с Discord объектами,
форматирования данных и других утилитарных операций.
"""

import re
from typing import Optional, Tuple
from datetime import datetime, timezone


def parse_emoji(emoji: str) -> Tuple[Optional[str], Optional[int], bool]:
    """Парсить эмодзи из строки Discord формата.
    
    Парсит строку эмодзи в формате Discord (<:name:id> или <a:name:id>)
    и возвращает компоненты.
    
    Args:
        emoji: Строка эмодзи в формате Discord или Unicode
    
    Returns:
        Tuple[Optional[str], Optional[int], bool]: 
            - Имя эмодзи (None для Unicode)
            - ID эмодзи (None для Unicode)
            - Анимирован ли эмодзи
    
    Examples:
        >>> parse_emoji("<:name:123456789>")
        ('name', 123456789, False)
        >>> parse_emoji("<a:name:123456789>")
        ('name', 123456789, True)
        >>> parse_emoji("👍")
        (None, None, False)
    """
    match = re.match(r'<(a?):(\w+):(\d+)>', emoji)
    if match:
        animated = bool(match.group(1))
        name = match.group(2)
        emoji_id = int(match.group(3))
        return name, emoji_id, animated
    return None, None, False


def format_emoji(name: str, emoji_id: int, animated: bool = False) -> str:
    """Форматировать эмодзи в строку Discord формата.
    
    Создает строку эмодзи в формате Discord из компонентов.
    
    Args:
        name: Имя эмодзи
        emoji_id: ID эмодзи
        animated: Анимирован ли эмодзи (по умолчанию: False)
    
    Returns:
        str: Строка эмодзи в формате Discord
    
    Example:
        >>> format_emoji("smile", 123456789, False)
        '<:smile:123456789>'
        >>> format_emoji("wave", 987654321, True)
        '<a:wave:987654321>'
    """
    prefix = "a" if animated else ""
    return f"<{prefix}:{name}:{emoji_id}>"


def snowflake_time(snowflake: int) -> datetime:
    """Получить время создания снежинки (Discord ID).
    
    Discord использует snowflake ID, которые содержат timestamp создания.
    Эта функция извлекает время создания из ID.
    
    Args:
        snowflake: Discord ID (snowflake)
    
    Returns:
        datetime: Время создания объекта в UTC
    
    Example:
        >>> snowflake_time(123456789012345678)
        datetime.datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    """
    timestamp = ((snowflake >> 22) + 1420070400000) / 1000
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def parse_timestamp(timestamp: str) -> datetime:
    """Парсить ISO timestamp в datetime.
    
    Парсит ISO 8601 timestamp (используется Discord) в объект datetime.
    
    Args:
        timestamp: ISO 8601 timestamp строка
    
    Returns:
        datetime: Объект datetime в UTC (или текущее время при ошибке)
    
    Example:
        >>> parse_timestamp("2021-01-01T00:00:00.000000+00:00")
        datetime.datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    """
    try:
        # Discord использует ISO 8601 формат
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except:
        return datetime.now(timezone.utc)


def escape_markdown(text: str) -> str:
    """Экранировать markdown символы в тексте.
    
    Экранирует специальные символы markdown, чтобы они отображались
    как обычный текст в Discord.
    
    Args:
        text: Текст для экранирования
    
    Returns:
        str: Текст с экранированными markdown символами
    
    Example:
        >>> escape_markdown("**bold** *italic*")
        '\\*\\*bold\\*\\* \\*italic\\*'
    """
    return re.sub(r'([*_`~|\\])', r'\\\1', text)


def clean_content(content: str, guild=None) -> str:
    """Очистить контент от упоминаний и специальных символов.
    
    Упрощенная версия функции очистки контента. Можно расширить
    для обработки упоминаний, эмодзи и других элементов.
    
    Args:
        content: Исходный контент
        guild: Объект гильдии (не используется в текущей реализации)
    
    Returns:
        str: Очищенный контент
    """
    # Упрощенная версия, можно расширить
    return content


def find_channel(channels, **kwargs):
    """Найти канал по параметрам.
    
    Ищет канал в списке каналов по указанным атрибутам.
    
    Args:
        channels: Итерируемый объект с каналами
        **kwargs: Атрибуты для поиска (например, name="general", type=0)
    
    Returns:
        Channel или None: Найденный канал или None
    
    Example:
        >>> channel = find_channel(guild.channels, name="general", type=0)
    """
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
    """Найти роль по параметрам.
    
    Ищет роль в списке ролей по указанным атрибутам.
    
    Args:
        roles: Итерируемый объект с ролями
        **kwargs: Атрибуты для поиска (например, name="Admin", id=123456)
    
    Returns:
        Role или None: Найденная роль или None
    
    Example:
        >>> role = find_role(guild.roles, name="Admin")
    """
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
    """Вычислить права участника в гильдии.
    
    Вычисляет итоговые права участника на основе его ролей.
    Владелец гильдии получает все права.
    
    Args:
        member: Объект участника (Member)
        guild: Объект гильдии (Guild)
    
    Returns:
        int: Битовая маска прав участника
    
    Note:
        Упрощенная версия. Для полной реализации нужно учитывать
        overwrites каналов и другие факторы.
    """
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
    """Проверить наличие права у участника.
    
    Проверяет, имеет ли участник указанное право в гильдии.
    
    Args:
        member: Объект участника (Member)
        guild: Объект гильдии (Guild)
        permission: Битовая маска права для проверки
    
    Returns:
        bool: True если участник имеет право, False иначе
    
    Example:
        >>> from discordself.permissions import Permissions
        >>> has_permission(member, guild, Permissions.SEND_MESSAGES)
        True
    """
    perms = calculate_permissions(member, guild)
    return (perms & permission) == permission

