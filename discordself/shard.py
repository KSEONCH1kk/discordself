"""Шардирование для Discord Gateway"""

import asyncio
import logging
from typing import List, Optional, Dict
from .gateway import GatewayClient
from .exceptions import ShardException

logger = logging.getLogger(__name__)


class Shard:
    """Один шард Gateway соединения"""
    
    def __init__(self, shard_id: int, shard_count: int, token: str, intents: int = 0):
        self.shard_id = shard_id
        self.shard_count = shard_count
        self.token = token
        self.intents = intents
        self.gateway: Optional[GatewayClient] = None
        self.running = False
    
    async def connect(self, gateway_url: Optional[str] = None, pending_handlers: Optional[Dict] = None):
        """Подключить шард"""
        self.gateway = GatewayClient(self.token, self.intents)
        self.gateway.shard_id = self.shard_id
        self.gateway.shard_count = self.shard_count
        
        # Применить обработчики ДО подключения
        if pending_handlers:
       #     print(f"🔵 Applying {len(pending_handlers)} event types to shard {self.shard_id}")
            for event_name, handlers in pending_handlers.items():
         #       print(f"🔵 Registering {len(handlers)} handlers for '{event_name}' in shard {self.shard_id}")
                for handler in handlers:
                    self.gateway.event(event_name)(handler)
        else:
            print(f"⚠️ No pending handlers to apply to shard {self.shard_id}")
        
        await self.gateway.connect(gateway_url)
        self.running = True
    
    async def disconnect(self):
        """Отключить шард"""
        self.running = False
        if self.gateway:
            await self.gateway.disconnect()
    
    def get_gateway(self) -> GatewayClient:
        """Получить Gateway клиент"""
        if not self.gateway:
            raise ShardException(f"Shard {self.shard_id} is not connected")
        return self.gateway


class ShardManager:
    """Менеджер шардов"""
    
    def __init__(self, token: str, shard_count: int = 1, intents: int = 0):
        self.token = token
        self.shard_count = shard_count
        self.intents = intents
        self.shards: List[Shard] = []
        self.gateway_url: Optional[str] = None
        self._pending_handlers: Dict[str, List] = {}
    
    async def start(self, gateway_url: Optional[str] = None):
        """Запустить все шарды"""
        self.gateway_url = gateway_url
        
        # Создать шарды
        for shard_id in range(self.shard_count):
            shard = Shard(shard_id, self.shard_count, self.token, self.intents)
            self.shards.append(shard)
        
        # Подключить шарды с задержкой
        for shard in self.shards:
            try:
                # Передать обработчики при подключении
                await shard.connect(self.gateway_url, self._pending_handlers)
                logger.info(f"Shard {shard.shard_id} connected")
           #     print(f"🔵 Shard {shard.shard_id} connected")
                
                # Задержка между подключениями шардов
                if shard.shard_id < len(self.shards) - 1:
                    await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Failed to connect shard {shard.shard_id}: {e}")
                print(f"❌ Failed to connect shard {shard.shard_id}: {e}")
                import traceback
                traceback.print_exc()
    
    async def stop(self):
        """Остановить все шарды"""
        for shard in self.shards:
            try:
                await shard.disconnect()
                logger.info(f"Shard {shard.shard_id} disconnected")
            except Exception as e:
                logger.error(f"Failed to disconnect shard {shard.shard_id}: {e}")
    
    def get_shard(self, shard_id: int) -> Shard:
        """Получить шард по ID"""
        if shard_id >= len(self.shards):
            raise ShardException(f"Shard {shard_id} does not exist")
        return self.shards[shard_id]
    
    def get_shard_for_guild(self, guild_id: int) -> Shard:
        """Получить шард для гильдии"""
        shard_id = (guild_id >> 22) % self.shard_count
        return self.get_shard(shard_id)
    
    def register_event_handler(self, event_name: str, handler):
        """Зарегистрировать обработчик события для всех шардов"""
        # Сохранить для будущих шардов
        if event_name not in self._pending_handlers:
            self._pending_handlers[event_name] = []
        self._pending_handlers[event_name].append(handler)
        
        # Применить к существующим шардам
        for shard in self.shards:
            if shard.gateway:
                shard.gateway.event(event_name)(handler)
    
    def register_event_handler_for_all(self, event_name: str, handler):
        """Зарегистрировать обработчик события для всех будущих шардов"""
        # Сохранить обработчик для будущих шардов
        if not hasattr(self, '_pending_handlers'):
            self._pending_handlers = {}
        if event_name not in self._pending_handlers:
            self._pending_handlers[event_name] = []
        self._pending_handlers[event_name].append(handler)
        
        # Применить к существующим шардам
        for shard in self.shards:
            if shard.gateway:
                shard.gateway.event(event_name)(handler)

