"""WebSocket клиент для Discord Gateway"""

import asyncio
import json
import logging
import time
import zlib
from typing import Dict, Optional, Callable, Any
import websockets
from .exceptions import WebSocketException
from .enums import GatewayOpcode

logger = logging.getLogger(__name__)


class GatewayClient:
    """WebSocket клиент для Discord Gateway"""
    
    def __init__(self, token: str, intents: int = 0):
        self.token = token
        self.intents = intents
        self.ws = None
        self.session_id: Optional[str] = None
        self.sequence: Optional[int] = None
        self.gateway_url: Optional[str] = None
        self.heartbeat_interval: Optional[float] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.listen_task: Optional[asyncio.Task] = None
        self.running = False
        self.event_handlers: Dict[str, list[Callable]] = {}
        self._zlib = zlib.decompressobj()
        self._buffer = bytearray()
        self.shard_id: Optional[int] = None
        self.shard_count: Optional[int] = None
    
    def event(self, name: str):
        """Декоратор для регистрации обработчика события"""
        def decorator(func: Callable):
            if name not in self.event_handlers:
                self.event_handlers[name] = []
            self.event_handlers[name].append(func)
            return func
        return decorator
    
    def dispatch(self, event_name: str, *args, **kwargs):
        """Вызвать обработчики события"""
        handlers = self.event_handlers.get(event_name, [])
        for handler in handlers:
            try:
            #    print(f"🔵 Calling handler {handler.__name__ if hasattr(handler, '__name__') else type(handler).__name__} for '{event_name}'")
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(*args, **kwargs))
                else:
                    handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in event handler {event_name}: {e}", exc_info=True)
                print(f"❌ Error in Gateway event handler {event_name}: {e}")
                import traceback
                traceback.print_exc()
    
    async def connect(self, gateway_url: Optional[str] = None):
        """Подключиться к Gateway"""
        if gateway_url:
            self.gateway_url = gateway_url
        else:
            # Получить Gateway URL (обычно это делается через HTTP)
            self.gateway_url = "wss://gateway.discord.gg/?v=10&encoding=json&compress=zlib-stream"
        
       # logger.info(f"Connecting to Gateway: {self.gateway_url}")
     #   print(f"🔵 Connecting to Gateway: {self.gateway_url}")
        
        try:
            self.ws = await websockets.connect(self.gateway_url)
            self.running = True
        #    print("🔵 WebSocket connected, starting listener...")
            
            # Запустить задачи
            self.listen_task = asyncio.create_task(self._listen())
            
            # Ждем HELLO
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Failed to connect to Gateway: {e}")
            print(f"❌ Failed to connect to Gateway: {e}")
            import traceback
            traceback.print_exc()
            raise WebSocketException(0, str(e))
    
    async def disconnect(self):
        """Отключиться от Gateway"""
        self.running = False
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if self.listen_task:
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass
        
        if self.ws:
            await self.ws.close()
            self.ws = None
    
    async def _listen(self):
        """Слушать сообщения от Gateway"""
   #     print("🔵 _listen started")
        while self.running and self.ws:
            try:
         #       print("🔵 Waiting for message...")
                message = await self.ws.recv()
         #       print(f"🔵 Received message type: {type(message)}, length: {len(message) if isinstance(message, bytes) else len(str(message))}")
                
                if isinstance(message, bytes):
                    # Декомпрессия zlib
                    self._buffer.extend(message)
                    # Проверка на конец потока (zlib stream)
                    if len(message) < 4 or message[-4:] != b'\x00\x00\xff\xff':
                  #      print("🔵 Partial zlib message, waiting for more...")
                        continue
                    
                    try:
                   #     print("🔵 Decompressing zlib message...")
                        decompressed = self._zlib.decompress(self._buffer)
                        self._buffer = bytearray()
                        message = decompressed.decode('utf-8')
                   #     print(f"🔵 Decompressed message: {message[:100]}...")
                    except Exception as decomp_error:
                        print(f"❌ Decompression error: {decomp_error}")
                        logger.error(f"Decompression error: {decomp_error}")
                        # Сбросить буфер и попробовать заново
                        self._buffer = bytearray()
                        self._zlib = zlib.decompressobj()
                        continue
                
           #     print(f"🔵 Parsing JSON message...")
                data = json.loads(message)
           #     print(f"🔵 Message opcode: {data.get('op')}, event: {data.get('t')}")
                await self._handle_message(data)
                
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"WebSocket connection closed: code={e.code}, reason={e.reason}")
                print(f"⚠️ WebSocket connection closed: code={e.code}, reason={e.reason}")
                if self.running:
                    # Попытка переподключения
                    print("🔄 Attempting to reconnect in 5 seconds...")
                    await asyncio.sleep(5)
                    try:
                        await self.connect(self.gateway_url)
                    except Exception as reconnect_error:
                        print(f"❌ Reconnection failed: {reconnect_error}")
                        logger.error(f"Reconnection failed: {reconnect_error}")
                break
            except Exception as e:
                logger.error(f"Error in _listen: {e}", exc_info=True)
                print(f"❌ Error in _listen: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(1)
    
    async def _handle_message(self, data: Dict):
        """Обработать сообщение от Gateway"""
        op = data.get("op")
        event_data = data.get("d")
        event_name = data.get("t")
        sequence = data.get("s")
        
        if sequence:
            self.sequence = sequence
        
        if op == GatewayOpcode.HELLO:
            self.heartbeat_interval = event_data.get("heartbeat_interval") / 1000.0
       #     logger.info(f"Received HELLO, heartbeat interval: {self.heartbeat_interval}s")
        #    print(f"🔵 Received HELLO, heartbeat interval: {self.heartbeat_interval}s")
            
            # Отправить IDENTIFY
            await self._identify()
            
            # Запустить heartbeat
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        elif op == GatewayOpcode.HEARTBEAT_ACK:
            pass
        
        elif op == GatewayOpcode.RECONNECT:
            logger.warning("Gateway requested reconnect")
        #    print("⚠️ Gateway requested reconnect")
            await self.disconnect()
            await asyncio.sleep(1)
            await self.connect(self.gateway_url)
        
        elif op == GatewayOpcode.INVALID_SESSION:
            logger.warning("Invalid session, re-identifying")
        #    print("⚠️ Invalid session, re-identifying in 5 seconds...")
            await asyncio.sleep(5)
            await self._identify()
        
        elif op == GatewayOpcode.DISPATCH:
            # Обработать событие
            if event_name == "READY":
                self.session_id = event_data.get("session_id")
           #     logger.info("Received READY event")
                print("🔵 READY event received in Gateway")
            
            if event_name == "MESSAGE_CREATE":
                print(f"🔵🔵🔵 Gateway received MESSAGE_CREATE: content={event_data.get('content', '')[:50] if event_data else 'None'}")
                print(f"🔵🔵🔵 Gateway dispatching to {len(self.event_handlers.get(event_name, []))} handlers")
                print(f"🔵🔵🔵 Gateway handlers: {[h.__name__ if hasattr(h, '__name__') else str(h) for h in self.event_handlers.get(event_name, [])]}")
            self.dispatch(event_name, event_data)
            self.dispatch("raw_socket_receive", event_name, event_data)
    
    async def _identify(self):
        """Отправить IDENTIFY"""
        payload = {
            "op": GatewayOpcode.IDENTIFY,
            "d": {
                "token": self.token,
                "properties": {
                    "os": "Windows",
                    "browser": "DiscordSelf",
                    "device": "DiscordSelf"
                },
                "intents": self.intents
            }
        }
        await self.send(payload)
        logger.info("Sent IDENTIFY")
    
    async def _heartbeat_loop(self):
        """Цикл отправки heartbeat"""
        while self.running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                if self.running:
                    await self._heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
    
    async def _heartbeat(self):
        """Отправить heartbeat"""
        payload = {
            "op": GatewayOpcode.HEARTBEAT,
            "d": self.sequence
        }
        await self.send(payload)
    
    async def send(self, payload: Dict):
        """Отправить сообщение в Gateway"""
        if self.ws:
            try:
                await self.ws.send(json.dumps(payload))
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                raise WebSocketException(0, str(e))
    
    async def update_presence(
        self,
        status: str = "online",
        activities: Optional[list] = None,
        since: Optional[int] = None,
        afk: bool = False
    ):
        """Обновить статус присутствия"""
        if activities is None:
            activities = []
        
        # Поддержка Status enum
        status_value = status.value if hasattr(status, 'value') else status
        
        payload = {
            "op": GatewayOpcode.PRESENCE_UPDATE,
            "d": {
                "since": since or int(time.time() * 1000),
                "activities": activities,
                "status": status_value,
                "afk": afk
            }
        }
        await self.send(payload)
    
    async def request_guild_members(self, guild_id: int, query: str = "", limit: int = 0):
        """Запросить участников гильдии"""
        payload = {
            "op": GatewayOpcode.REQUEST_GUILD_MEMBERS,
            "d": {
                "guild_id": str(guild_id),
                "query": query,
                "limit": limit
            }
        }
        await self.send(payload)
    
    async def resume(self):
        """Возобновить сессию"""
        if not self.session_id or not self.sequence:
            raise WebSocketException(0, "Cannot resume without session_id and sequence")
        
        payload = {
            "op": GatewayOpcode.RESUME,
            "d": {
                "token": self.token,
                "session_id": self.session_id,
                "seq": self.sequence
            }
        }
        await self.send(payload)

