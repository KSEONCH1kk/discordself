"""Система кэширования для Discord объектов"""

import time
from typing import Dict, Optional, Any, TypeVar, Generic
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Cache(Generic[T]):
    """LRU кэш с TTL"""
    
    def __init__(self, max_size: int = 10000, ttl: Optional[float] = None):
        self.max_size = max_size
        self.ttl = ttl  # Time to live в секундах
        self._cache: OrderedDict[str, tuple[T, float]] = OrderedDict()
    
    def get(self, key: str) -> Optional[T]:
        """Получить значение из кэша"""
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
        """Установить значение в кэш"""
        if key in self._cache:
            self._cache.move_to_end(key)
        
        self._cache[key] = (value, time.time())
        
        # Удалить старые записи если превышен размер
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
    
    def delete(self, key: str):
        """Удалить значение из кэша"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """Очистить кэш"""
        self._cache.clear()
    
    def __len__(self) -> int:
        return len(self._cache)


class CacheManager:
    """Менеджер кэшей для различных типов объектов"""
    
    def __init__(self):
        self.users = Cache(max_size=10000)
        self.guilds = Cache(max_size=1000)
        self.channels = Cache(max_size=10000)
        self.messages = Cache(max_size=5000, ttl=3600)  # 1 час TTL для сообщений
        self.members = Cache(max_size=50000)
        self.roles = Cache(max_size=10000)
        self.emojis = Cache(max_size=5000)
    
    def clear(self):
        """Очистить все кэши"""
        self.users.clear()
        self.guilds.clear()
        self.channels.clear()
        self.messages.clear()
        self.members.clear()
        self.roles.clear()
        self.emojis.clear()
    
    def get_user(self, user_id: str):
        """Получить пользователя из кэша"""
        return self.users.get(user_id)
    
    def set_user(self, user_id: str, user_data: Dict):
        """Сохранить пользователя в кэш"""
        self.users.set(user_id, user_data)
    
    def get_guild(self, guild_id: str):
        """Получить гильдию из кэша"""
        return self.guilds.get(guild_id)
    
    def set_guild(self, guild_id: str, guild_data: Dict):
        """Сохранить гильдию в кэш"""
        self.guilds.set(guild_id, guild_data)
    
    def get_channel(self, channel_id: str):
        """Получить канал из кэша"""
        return self.channels.get(channel_id)
    
    def set_channel(self, channel_id: str, channel_data: Dict):
        """Сохранить канал в кэш"""
        self.channels.set(channel_id, channel_data)
    
    def get_message(self, message_id: str):
        """Получить сообщение из кэша"""
        return self.messages.get(message_id)
    
    def set_message(self, message_id: str, message_data: Dict):
        """Сохранить сообщение в кэш"""
        self.messages.set(message_id, message_data)
    
    def get_member(self, guild_id: str, user_id: str):
        """Получить участника из кэша"""
        key = f"{guild_id}:{user_id}"
        return self.members.get(key)
    
    def set_member(self, guild_id: str, user_id: str, member_data: Dict):
        """Сохранить участника в кэш"""
        key = f"{guild_id}:{user_id}"
        self.members.set(key, member_data)
    
    def get_role(self, role_id: str):
        """Получить роль из кэша"""
        return self.roles.get(role_id)
    
    def set_role(self, role_id: str, role_data: Dict):
        """Сохранить роль в кэш"""
        self.roles.set(role_id, role_data)
    
    def get_emoji(self, emoji_id: str):
        """Получить эмодзи из кэша"""
        return self.emojis.get(emoji_id)
    
    def set_emoji(self, emoji_id: str, emoji_data: Dict):
        """Сохранить эмодзи в кэш"""
        self.emojis.set(emoji_id, emoji_data)

