"""Система кэширования для Discord объектов.

Этот модуль предоставляет систему кэширования с поддержкой
LRU (Least Recently Used) алгоритма и TTL (Time To Live).
"""

import time
from typing import Dict, Optional, Any, TypeVar, Generic
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Cache(Generic[T]):
    """LRU кэш с поддержкой TTL.
    
    Реализует кэш с алгоритмом LRU (Least Recently Used) и опциональным
    TTL (Time To Live) для автоматического удаления устаревших записей.
    
    Args:
        max_size: Максимальный размер кэша (по умолчанию: 10000)
        ttl: Время жизни записей в секундах (по умолчанию: None, без ограничений)
    
    Example:
        ```python
        cache = Cache(max_size=1000, ttl=3600)  # 1 час TTL
        cache.set("key", "value")
        value = cache.get("key")
        ```
    """
    
    def __init__(self, max_size: int = 10000, ttl: Optional[float] = None):
        self.max_size = max_size
        self.ttl = ttl  # Time to live в секундах
        self._cache: OrderedDict[str, tuple[T, float]] = OrderedDict()
    
    def get(self, key: str) -> Optional[T]:
        """Получить значение из кэша.
        
        Args:
            key: Ключ для поиска
        
        Returns:
            Optional[T]: Значение из кэша или None если не найдено или истек TTL
        """
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        
        # Проверка TTL
        if self.ttl and time.time() - timestamp > self.ttl:
            del self._cache[key]
            return None
        
        # Переместить в конец (LRU)
        self._cache.move_to_end(key)
        return value
    
    def set(self, key: str, value: T):
        """Установить значение в кэш.
        
        Если кэш переполнен, удаляется наименее используемый элемент.
        
        Args:
            key: Ключ для сохранения
            value: Значение для сохранения
        """
        if key in self._cache:
            self._cache.move_to_end(key)
        
        self._cache[key] = (value, time.time())
        
        # Удалить старые записи если превышен размер
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
    
    def delete(self, key: str):
        """Удалить значение из кэша.
        
        Args:
            key: Ключ для удаления
        """
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """Очистить весь кэш.
        
        Удаляет все записи из кэша.
        """
        self._cache.clear()
    
    def __len__(self) -> int:
        return len(self._cache)


class CacheManager:
    """Менеджер кэшей для различных типов Discord объектов.
    
    Управляет отдельными кэшами для пользователей, гильдий, каналов,
    сообщений, участников, ролей и эмодзи.
    
    Attributes:
        users: Кэш пользователей (max_size=10000)
        guilds: Кэш гильдий (max_size=1000)
        channels: Кэш каналов (max_size=10000)
        messages: Кэш сообщений (max_size=5000, ttl=3600)
        members: Кэш участников (max_size=50000)
        roles: Кэш ролей (max_size=10000)
        emojis: Кэш эмодзи (max_size=5000)
    """
    
    def __init__(self):
        self.users = Cache(max_size=10000)
        self.guilds = Cache(max_size=1000)
        self.channels = Cache(max_size=10000)
        self.messages = Cache(max_size=5000, ttl=3600)  # 1 час TTL для сообщений
        self.members = Cache(max_size=50000)
        self.roles = Cache(max_size=10000)
        self.emojis = Cache(max_size=5000)
    
    def clear(self):
        """Очистить все кэши.
        
        Удаляет все записи из всех кэшей.
        """
        self.users.clear()
        self.guilds.clear()
        self.channels.clear()
        self.messages.clear()
        self.members.clear()
        self.roles.clear()
        self.emojis.clear()
    
    def get_user(self, user_id: str):
        """Получить пользователя из кэша.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Optional[Dict]: Данные пользователя или None
        """
        return self.users.get(user_id)
    
    def set_user(self, user_id: str, user_data: Dict):
        """Сохранить пользователя в кэш.
        
        Args:
            user_id: ID пользователя
            user_data: Данные пользователя
        """
        self.users.set(user_id, user_data)
    
    def get_guild(self, guild_id: str):
        """Получить гильдию из кэша.
        
        Args:
            guild_id: ID гильдии
        
        Returns:
            Optional[Dict]: Данные гильдии или None
        """
        return self.guilds.get(guild_id)
    
    def set_guild(self, guild_id: str, guild_data: Dict):
        """Сохранить гильдию в кэш.
        
        Args:
            guild_id: ID гильдии
            guild_data: Данные гильдии
        """
        self.guilds.set(guild_id, guild_data)
    
    def get_channel(self, channel_id: str):
        """Получить канал из кэша.
        
        Args:
            channel_id: ID канала
        
        Returns:
            Optional[Dict]: Данные канала или None
        """
        return self.channels.get(channel_id)
    
    def set_channel(self, channel_id: str, channel_data: Dict):
        """Сохранить канал в кэш.
        
        Args:
            channel_id: ID канала
            channel_data: Данные канала
        """
        self.channels.set(channel_id, channel_data)
    
    def get_message(self, message_id: str):
        """Получить сообщение из кэша.
        
        Args:
            message_id: ID сообщения
        
        Returns:
            Optional[Dict]: Данные сообщения или None
        """
        return self.messages.get(message_id)
    
    def set_message(self, message_id: str, message_data: Dict):
        """Сохранить сообщение в кэш.
        
        Args:
            message_id: ID сообщения
            message_data: Данные сообщения
        """
        self.messages.set(message_id, message_data)
    
    def get_member(self, guild_id: str, user_id: str):
        """Получить участника из кэша.
        
        Args:
            guild_id: ID гильдии
            user_id: ID пользователя
        
        Returns:
            Optional[Dict]: Данные участника или None
        """
        key = f"{guild_id}:{user_id}"
        return self.members.get(key)
    
    def set_member(self, guild_id: str, user_id: str, member_data: Dict):
        """Сохранить участника в кэш.
        
        Args:
            guild_id: ID гильдии
            user_id: ID пользователя
            member_data: Данные участника
        """
        key = f"{guild_id}:{user_id}"
        self.members.set(key, member_data)
    
    def get_role(self, role_id: str):
        """Получить роль из кэша.
        
        Args:
            role_id: ID роли
        
        Returns:
            Optional[Dict]: Данные роли или None
        """
        return self.roles.get(role_id)
    
    def set_role(self, role_id: str, role_data: Dict):
        """Сохранить роль в кэш.
        
        Args:
            role_id: ID роли
            role_data: Данные роли
        """
        self.roles.set(role_id, role_data)
    
    def get_emoji(self, emoji_id: str):
        """Получить эмодзи из кэша.
        
        Args:
            emoji_id: ID эмодзи
        
        Returns:
            Optional[Dict]: Данные эмодзи или None
        """
        return self.emojis.get(emoji_id)
    
    def set_emoji(self, emoji_id: str, emoji_data: Dict):
        """Сохранить эмодзи в кэш.
        
        Args:
            emoji_id: ID эмодзи
            emoji_data: Данные эмодзи
        """
        self.emojis.set(emoji_id, emoji_data)

