"""Rate-limit менеджер для Discord API"""

import time
import asyncio
from collections import defaultdict
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Менеджер rate limits для Discord API"""
    
    def __init__(self):
        self.buckets: Dict[str, 'Bucket'] = {}
        self.global_ratelimit: Optional[float] = None
        self.lock = asyncio.Lock()
    
    async def acquire(self, route: str, method: str = "GET"):
        """Получить разрешение на выполнение запроса"""
        async with self.lock:
            # Проверка глобального rate limit
            if self.global_ratelimit:
                wait_time = self.global_ratelimit - time.time()
                if wait_time > 0:
                    logger.warning(f"Global rate limit active, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    self.global_ratelimit = None
            
            # Получить bucket для маршрута
            bucket_key = self._get_bucket_key(route, method)
            bucket = self.buckets.get(bucket_key)
            
            if bucket is None:
                bucket = Bucket(bucket_key)
                self.buckets[bucket_key] = bucket
            
            await bucket.acquire()
    
    def update_ratelimit(self, route: str, method: str, headers: Dict):
        """Обновить информацию о rate limit из заголовков ответа"""
        bucket_key = self._get_bucket_key(route, method)
        bucket = self.buckets.get(bucket_key)
        
        if bucket is None:
            bucket = Bucket(bucket_key)
            self.buckets[bucket_key] = bucket
        
        # Обновить bucket из заголовков
        remaining = headers.get('X-RateLimit-Remaining')
        reset_after = headers.get('X-RateLimit-Reset-After')
        limit = headers.get('X-RateLimit-Limit')
        retry_after = headers.get('Retry-After')
        
        if retry_after:
            # Глобальный rate limit
            self.global_ratelimit = time.time() + float(retry_after)
            logger.warning(f"Global rate limit hit, retry after {retry_after}s")
        
        if reset_after:
            bucket.reset_after = float(reset_after)
        
        if limit:
            bucket.limit = int(limit)
        
        if remaining:
            bucket.remaining = int(remaining)
    
    def _get_bucket_key(self, route: str, method: str) -> str:
        """Получить ключ bucket для маршрута"""
        # Упрощенная логика bucket key
        # В реальности Discord использует более сложную логику
        route = route.replace('/api/v10', '')
        
        # Удалить ID из маршрута для группировки
        parts = route.split('/')
        key_parts = []
        
        for part in parts:
            if part.isdigit() or part in ['@me', '@guild']:
                key_parts.append('{}')
            else:
                key_parts.append(part)
        
        return f"{method}:{':'.join(key_parts)}"


class Bucket:
    """Bucket для rate limiting"""
    
    def __init__(self, key: str):
        self.key = key
        self.limit = 50  # По умолчанию
        self.remaining = 50
        self.reset_after = 0.0
        self.reset_at = 0.0
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Получить разрешение на запрос"""
        async with self.lock:
            current_time = time.time()
            
            # Если bucket был сброшен
            if current_time >= self.reset_at:
                self.remaining = self.limit
                self.reset_at = current_time + self.reset_after
            
            # Если нет доступных запросов, ждем
            if self.remaining <= 0:
                wait_time = self.reset_at - current_time
                if wait_time > 0:
                    logger.info(f"Rate limit bucket {self.key} exhausted, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    self.remaining = self.limit
                    self.reset_at = current_time + self.reset_after
            
            self.remaining -= 1

