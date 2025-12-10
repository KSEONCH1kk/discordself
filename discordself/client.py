"""Основной клиент Discord Selfbot"""

import asyncio
import logging
from typing import Optional, Dict, List, Callable, Tuple
from .http import HTTPClient
from .gateway import GatewayClient
from .shard import ShardManager
from .cache import CacheManager
from .models import User, Guild, Channel, Message, Member, Role, Emoji
from .exceptions import LoginFailure
from .enums import Status, ActivityType

logger = logging.getLogger(__name__)


class Client:
    """Основной клиент для Discord Selfbot"""
    
    def __init__(
        self,
        token: str,
        shard_count: int = 1,
        intents: int = 0,
        enable_cache: bool = True
    ):
        self.token = token
        self.shard_count = shard_count
        self.intents = intents
        self.enable_cache = enable_cache
        
        # Клиенты
        self.http: Optional[HTTPClient] = None
        self.shard_manager: Optional[ShardManager] = None
        
        # Кэш
        self.cache = CacheManager() if enable_cache else None
        
        # Данные
        self.user: Optional[User] = None
        self.guilds: Dict[int, Guild] = {}
        self.channels: Dict[int, Channel] = {}
        
        # Voice
        self.voice_clients: Dict[int, 'VoiceClient'] = {}  # guild_id -> VoiceClient
        
        # Обработчики событий
        self.event_handlers: Dict[str, List[Callable]] = {}
        self._event_handlers: Dict[str, List[Tuple[Callable, int]]] = {}  # С приоритетами: [(handler, priority), ...]
        
        # Состояние
        self._closed = False
    
    def event(self, name: Optional[str] = None):
        """Декоратор для регистрации обработчика события
        
        Использование:
            @client.event("ready")
            async def on_ready():
                ...
            
            @client.listen("message")
            async def on_message(message):
                ...
        """
        def decorator(func):
            event_name = name or func.__name__
            if event_name not in self.event_handlers:
                self.event_handlers[event_name] = []
            self.event_handlers[event_name].append(func)
            return func
        if callable(name):
            # Использование как @client.event без скобок
            func = name
            event_name = func.__name__
            if event_name not in self.event_handlers:
                self.event_handlers[event_name] = []
            self.event_handlers[event_name].append(func)
            return func
        return decorator
    
    def listen(self, name: Optional[str] = None, priority: int = 0):
        """Декоратор для регистрации listener (аналог discord.py)
        
        Использование:
            @client.listen("message")
            async def on_message(message):
                ...
            
            @client.listen("ready", priority=1)
            async def on_ready_high_priority():
                ...
        """
        def decorator(func):
            event_name = name or func.__name__
            if event_name not in self._event_handlers:
                self._event_handlers[event_name] = []
            self._event_handlers[event_name].append((func, priority))
            # Сортировать по приоритету (больше = выше)
            self._event_handlers[event_name].sort(key=lambda x: x[1], reverse=True)
            # Также добавить в старую систему для совместимости
            if event_name not in self.event_handlers:
                self.event_handlers[event_name] = []
            self.event_handlers[event_name].append(func)
            return func
        if callable(name):
            # Использование как @client.listen без скобок
            func = name
            event_name = func.__name__
            if event_name not in self._event_handlers:
                self._event_handlers[event_name] = []
            self._event_handlers[event_name].append((func, 0))
            if event_name not in self.event_handlers:
                self.event_handlers[event_name] = []
            self.event_handlers[event_name].append(func)
            return func
        return decorator
    
    def dispatch(self, event_name: str, *args, **kwargs):
        """Вызвать обработчики события с поддержкой приоритетов"""
        # Обработчики с приоритетами (новые listeners)
        priority_handlers = self._event_handlers.get(event_name, [])
        print(f"🔵 dispatch({event_name}): priority_handlers={len(priority_handlers)}, event_handlers={len(self.event_handlers.get(event_name, []))}")
        for handler, priority in priority_handlers:
            try:
                print(f"🔵 Calling priority handler: {handler.__name__ if hasattr(handler, '__name__') else type(handler).__name__}")
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(*args, **kwargs))
                else:
                    handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in event handler {event_name}: {e}", exc_info=True)
                # Вызвать on_error если есть
                if hasattr(self, 'on_error'):
                    try:
                        if asyncio.iscoroutinefunction(self.on_error):
                            asyncio.create_task(self.on_error(event_name, *args, **kwargs))
                        else:
                            self.on_error(event_name, *args, **kwargs)
                    except:
                        pass
        
        # Старые обработчики (для совместимости)
        handlers = self.event_handlers.get(event_name, [])
        # Исключить дубликаты (уже обработанные в priority_handlers)
        priority_handler_funcs = {h for h, _ in priority_handlers}
        print(f"🔵 Calling {len(handlers)} regular handlers, excluding {len(priority_handler_funcs)} priority handlers")
        print(f"🔵 Handler functions: {[h.__name__ if hasattr(h, '__name__') else str(h) for h in handlers]}")
        print(f"🔵 Priority handler funcs: {[h.__name__ if hasattr(h, '__name__') else str(h) for h in priority_handler_funcs]}")
        for handler in handlers:
            if handler not in priority_handler_funcs:
                try:
                    print(f"🔵🔵🔵 About to call regular handler: {handler.__name__ if hasattr(handler, '__name__') else type(handler).__name__}, id={id(handler)}")
                    if asyncio.iscoroutinefunction(handler):
                        task = asyncio.create_task(handler(*args, **kwargs))
                        print(f"🔵🔵🔵 Created task for handler: {task}")
                    else:
                        result = handler(*args, **kwargs)
                        print(f"🔵🔵🔵 Handler returned: {result}")
                except Exception as e:
                    logger.error(f"Error in event handler {event_name}: {e}", exc_info=True)
                    # Вызвать on_error если есть
                    if hasattr(self, 'on_error'):
                        try:
                            if asyncio.iscoroutinefunction(self.on_error):
                                asyncio.create_task(self.on_error(event_name, *args, **kwargs))
                            else:
                                self.on_error(event_name, *args, **kwargs)
                        except:
                            pass
    
    async def login(self):
        """Войти в аккаунт"""
        try:
            self.http = HTTPClient(self.token)
            await self.http.start()
            
            # Получить информацию о пользоватеle
            user_data = await self.http.get_current_user()
            self.user = User(user_data, self)
            
            logger.info(f"Logged in as {self.user}")
            
            # Сохранить в кэш
            if self.cache:
                self.cache.set_user(str(self.user.id), user_data)
            
            return self.user
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise LoginFailure(str(e))
    
    async def connect(self):
        """Подключиться к Gateway"""
        if not self.http:
            await self.login()
        
        # Получить Gateway URL
        try:
            gateway_data = await self.http.get_gateway_bot()
            gateway_url = gateway_data.get("url")
            shards = gateway_data.get("shards", self.shard_count)
            
            if shards != self.shard_count:
                logger.warning(f"Recommended shard count: {shards}, using {self.shard_count}")
        except:
            gateway_url = None
        
        # Создать шард менеджер
        self.shard_manager = ShardManager(self.token, self.shard_count, self.intents)
        
        # Зарегистрировать обработчики событий (сохраняются для будущих шардов)
        self._register_event_handlers()
        
        # Подключить шарды (обработчики применятся автоматически)
        await self.shard_manager.start(gateway_url)
        
        logger.info("Connected to Gateway")
    
    def _register_event_handlers(self):
        """Зарегистрировать обработчики событий для шардов"""
        # Регистрация всех событий из self.event_handlers
        for event_name, handlers in self.event_handlers.items():
            for handler in handlers:
                self.shard_manager.register_event_handler(event_name, handler)
        
        # Внутренние обработчики
        self.shard_manager.register_event_handler("READY", self._on_ready)
        self.shard_manager.register_event_handler("GUILD_CREATE", self._on_guild_create)
        self.shard_manager.register_event_handler("GUILD_UPDATE", self._on_guild_update)
        self.shard_manager.register_event_handler("GUILD_DELETE", self._on_guild_delete)
        self.shard_manager.register_event_handler("CHANNEL_CREATE", self._on_channel_create)
        self.shard_manager.register_event_handler("CHANNEL_UPDATE", self._on_channel_update)
        self.shard_manager.register_event_handler("CHANNEL_DELETE", self._on_channel_delete)
        self.shard_manager.register_event_handler("MESSAGE_CREATE", self._on_message_create)
        self.shard_manager.register_event_handler("MESSAGE_UPDATE", self._on_message_update)
        self.shard_manager.register_event_handler("MESSAGE_DELETE", self._on_message_delete)
        self.shard_manager.register_event_handler("VOICE_STATE_UPDATE", self._on_voice_state_update)
        self.shard_manager.register_event_handler("VOICE_SERVER_UPDATE", self._on_voice_server_update)
    
    async def _on_ready(self, data: Dict):
        """Обработчик события READY"""
        logger.info("Client is ready")
    #    print("🔵 READY event received in _on_ready")
        self.dispatch("ready")
    
    async def _on_guild_create(self, data: Dict):
        """Обработчик события GUILD_CREATE"""
        guild = Guild(data, self)
        self.guilds[guild.id] = guild
        
        if self.cache:
            self.cache.set_guild(str(guild.id), data)
        
        self.dispatch("guild_join", guild)
    
    async def _on_guild_update(self, data: Dict):
        """Обработчик события GUILD_UPDATE"""
        guild_id = int(data.get("id", 0))
        if guild_id in self.guilds:
            self.guilds[guild_id]._update(data)
            if self.cache:
                self.cache.set_guild(str(guild_id), data)
        self.dispatch("guild_update", self.guilds.get(guild_id))
    
    async def _on_guild_delete(self, data: Dict):
        """Обработчик события GUILD_DELETE"""
        guild_id = int(data.get("id", 0))
        guild = self.guilds.pop(guild_id, None)
        if self.cache:
            self.cache.guilds.delete(str(guild_id))
        self.dispatch("guild_remove", guild)
    
    async def _on_channel_create(self, data: Dict):
        """Обработчик события CHANNEL_CREATE"""
        channel = Channel(data, self.guilds.get(int(data.get("guild_id", 0))) if data.get("guild_id") else None, self)
        self.channels[channel.id] = channel
        
        if self.cache:
            self.cache.set_channel(str(channel.id), data)
        
        self.dispatch("channel_create", channel)
    
    async def _on_channel_update(self, data: Dict):
        """Обработчик события CHANNEL_UPDATE"""
        channel_id = int(data.get("id", 0))
        if channel_id in self.channels:
            self.channels[channel_id]._update(data)
            if self.cache:
                self.cache.set_channel(str(channel_id), data)
        self.dispatch("channel_update", self.channels.get(channel_id))
    
    async def _on_channel_delete(self, data: Dict):
        """Обработчик события CHANNEL_DELETE"""
        channel_id = int(data.get("id", 0))
        channel = self.channels.pop(channel_id, None)
        if self.cache:
            self.cache.channels.delete(str(channel_id))
        self.dispatch("channel_delete", channel)
    
    async def _on_message_create(self, data: Dict):
        """Обработчик события MESSAGE_CREATE"""
        print(f"🔵🔵🔵 _on_message_create CALLED! Content: {data.get('content', '')[:50]}")
        print(f"🔵🔵🔵 Message author: {data.get('author', {}).get('id')}, bot: {data.get('author', {}).get('bot', False)}")
        try:
            message = Message(data, self)
            print(f"🔵🔵🔵 Message object created successfully")
       #     print(f"🔵 Message object created: {message.content[:50] if message.content else 'empty'}")
            
            # Убедиться, что канал закэширован
            channel_id = message.channel_id
            if channel_id and channel_id not in self.channels:
                # Попытаться получить канал из кэша или создать задачу для его получения
                if self.cache:
                    cached_channel_data = self.cache.get_channel(str(channel_id))
                    if cached_channel_data:
                        guild_id = int(cached_channel_data.get("guild_id", 0)) if cached_channel_data.get("guild_id") else None
                        guild = self.guilds.get(guild_id) if guild_id else None
                        channel = Channel(cached_channel_data, guild, self)
                        self.channels[channel.id] = channel
                    else:
                        # Асинхронно получить канал, если его нет в кэше
                        asyncio.create_task(self._ensure_channel_cached(channel_id))
                else:
                    # Асинхронно получить канал
                    asyncio.create_task(self._ensure_channel_cached(channel_id))
            
            if self.cache:
                self.cache.set_message(str(message.id), data)
            
            print(f"🔵 Dispatching 'message' event to {len(self.event_handlers.get('message', []))} handlers")
            print(f"🔵 Dispatching 'message_create' event to {len(self.event_handlers.get('message_create', []))} handlers")
            print(f"🔵 Message content: {message.content[:50] if message.content else 'None'}")
            print(f"🔵 About to call dispatch('message')...")
            self.dispatch("message", message)
            print(f"🔵 dispatch('message') returned")
            self.dispatch("message_create", message)
        except Exception as e:
            print(f"❌ Error in _on_message_create: {e}")
            import traceback
            traceback.print_exc()
    
    async def _ensure_channel_cached(self, channel_id: int):
        """Убедиться, что канал закэширован"""
        try:
            if channel_id not in self.channels and self.http:
                await self.fetch_channel(channel_id)
        except Exception as e:
            logger.warning(f"Failed to fetch channel {channel_id}: {e}")
            print(f"⚠️ Failed to fetch channel {channel_id}: {e}")
    
    async def _on_message_update(self, data: Dict):
        """Обработчик события MESSAGE_UPDATE"""
        message_id = int(data.get("id", 0))
        message = self.cache.get_message(str(message_id)) if self.cache else None
        
        if message:
            message = Message(message, self)
            message._update(data)
            if self.cache:
                self.cache.set_message(str(message_id), data)
        else:
            message = Message(data, self)
        
        self.dispatch("message_update", message)
    
    async def _on_message_delete(self, data: Dict):
        """Обработчик события MESSAGE_DELETE"""
        message_id = int(data.get("id", 0))
        channel_id = int(data.get("channel_id", 0))
        
        if self.cache:
            self.cache.messages.delete(str(message_id))
        
        self.dispatch("message_delete", message_id, channel_id)
    
    async def _on_voice_state_update(self, data: Dict):
        """Обработчик события VOICE_STATE_UPDATE"""
        from .models import VoiceState
        from .voice import VoiceClient
        
        guild_id = int(data.get("guild_id", 0)) if data.get("guild_id") else None
        user_id = int(data.get("user_id", 0))
        channel_id = data.get("channel_id")
        session_id = data.get("session_id")
        
        # Если это наш пользователь, обновить VoiceClient
        if guild_id and self.user and user_id == self.user.id and guild_id in self.voice_clients:
            voice_client = self.voice_clients[guild_id]
            voice_client.session_id = session_id
            
            # Если канал None, удалить voice client
            if not channel_id:
                if guild_id in self.voice_clients:
                    await self.voice_clients[guild_id].disconnect()
                    del self.voice_clients[guild_id]
            # Не подключаться здесь - подключение произойдет в connect() после получения всех данных
        elif guild_id and self.user and user_id == self.user.id:
            logger.warning(f"⚠️ VOICE_STATE_UPDATE for our user but no voice_client for guild {guild_id}")
        
        # Создать VoiceState объект
        guild = self.guilds.get(guild_id) if guild_id else None
        voice_state = VoiceState(data, guild, self)
        
        self.dispatch("voice_state_update", voice_state)
    
    async def _on_voice_server_update(self, data: Dict):
        """Обработчик события VOICE_SERVER_UPDATE"""
        from .voice import VoiceClient
        
        guild_id = int(data.get("guild_id", 0))
        token = data.get("token")
        endpoint = data.get("endpoint")
        
        # Обновить VoiceClient если существует
        if guild_id in self.voice_clients:
            voice_client = self.voice_clients[guild_id]
            voice_client.token = token
            # Убрать wss:// префикс если есть
            if endpoint:
                if endpoint.startswith('wss://'):
                    endpoint = endpoint[6:]
                voice_client.endpoint = endpoint
        else:
            logger.warning(f"⚠️ VOICE_SERVER_UPDATE received but no voice client for guild {guild_id}")
        
        self.dispatch("voice_server_update", data)
    
    async def start(self):
        """Запустить клиент"""
        await self.login()
        await self.connect()
    
    async def close(self):
        """Закрыть клиент"""
        if self._closed:
            return
        
        self._closed = True
        
        try:
            if self.shard_manager:
                await self.shard_manager.stop()
        except Exception as e:
            logger.error(f"Error stopping shard manager: {e}")
        
        try:
            if self.http:
                await self.http.close()
        except Exception as e:
            logger.error(f"Error closing HTTP client: {e}")
        
        logger.info("Client closed")
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    # Утилитные методы
    
    def get_guild(self, guild_id: int) -> Optional[Guild]:
        """Получить гильдию по ID"""
        return self.guilds.get(guild_id)
    
    def get_channel(self, channel_id: int) -> Optional[Channel]:
        """Получить канал по ID"""
        return self.channels.get(channel_id)
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        if self.cache:
            user_data = self.cache.get_user(str(user_id))
            if user_data:
                return User(user_data, self)
        return None
    
    def get_voice_client(self, guild_id: int) -> Optional['VoiceClient']:
        """Получить VoiceClient для гильдии"""
        from .voice import VoiceClient
        return self.voice_clients.get(guild_id)
    
    async def fetch_guild(self, guild_id: int) -> Guild:
        """Получить гильдию с сервера"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        data = await self.http.get_guild(guild_id)
        guild = Guild(data, self)
        self.guilds[guild.id] = guild
        
        if self.cache:
            self.cache.set_guild(str(guild.id), data)
        
        return guild
    
    async def fetch_channel(self, channel_id: int) -> Channel:
        """Получить канал с сервера"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        data = await self.http.get_channel(channel_id)
        guild_id = int(data.get("guild_id", 0)) if data.get("guild_id") else None
        
        # Получить guild, если его нет в кэше
        guild = self.guilds.get(guild_id) if guild_id else None
        if guild_id and not guild:
            try:
                guild = await self.fetch_guild(guild_id)
            except Exception as e:
                logger.warning(f"Failed to fetch guild {guild_id} for channel {channel_id}: {e}")
        
        channel = Channel(data, guild, self)
        self.channels[channel.id] = channel
        
        if self.cache:
            self.cache.set_channel(str(channel.id), data)
        
        return channel
    
    async def fetch_message(self, channel_id: int, message_id: int) -> Message:
        """Получить сообщение с сервера"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        data = await self.http.get_message(channel_id, message_id)
        message = Message(data, self)
        
        if self.cache:
            self.cache.set_message(str(message.id), data)
        
        return message
    
    async def fetch_messages(
        self,
        channel_id: int,
        limit: int = 50,
        before: Optional[int] = None,
        after: Optional[int] = None,
        around: Optional[int] = None
    ) -> List[Message]:
        """Получить сообщения канала"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        data = await self.http.get_channel_messages(channel_id, limit, before, after, around)
        messages = [Message(msg, self) for msg in data]
        
        if self.cache:
            for msg in messages:
                self.cache.set_message(str(msg.id), msg.__dict__)
        
        return messages
    
    async def fetch_all_messages(
        self,
        channel_id: int,
        limit: Optional[int] = None,
        before: Optional[int] = None,
        after: Optional[int] = None,
        check: Optional[Callable] = None
    ) -> List[Message]:
        """Получить все сообщения канала с пагинацией"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        data = await self.http.get_all_channel_messages(channel_id, limit, before, after, check)
        messages = [Message(msg, self) for msg in data]
        
        if self.cache:
            for msg in messages:
                self.cache.set_message(str(msg.id), msg.__dict__)
        
        return messages
    
    async def search_messages(
        self,
        guild_id: int,
        channel_id: Optional[int] = None,
        author_id: Optional[int] = None,
        mentions: Optional[int] = None,
        has: Optional[str] = None,
        min_id: Optional[int] = None,
        max_id: Optional[int] = None,
        limit: int = 25,
        offset: int = 0
    ) -> Dict:
        """Поиск сообщений в гильдии"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        return await self.http.search_messages(
            channel_id, guild_id, author_id, mentions,
            has, min_id, max_id, limit, offset
        )
    
    async def change_presence(
        self,
        status: Status = Status.ONLINE,
        activities: Optional[List[Dict]] = None,
        afk: bool = False
    ):
        """Изменить статус присутствия"""
        if not self.shard_manager:
            raise RuntimeError("Not connected to Gateway")
        
        for shard in self.shard_manager.shards:
            if shard.gateway:
                await shard.gateway.update_presence(status, activities, None, afk)
    
    # Методы для работы с сообщениями
    
    async def send_message(
        self,
        channel_id: int,
        content: Optional[str] = None,
        embeds: Optional[list] = None,
        components: Optional[list] = None,
        files: Optional[list] = None,
        allowed_mentions: Optional[Dict] = None,
        message_reference: Optional[Dict] = None,
        stickers: Optional[list] = None,
        flags: Optional[int] = None,
        **kwargs
    ) -> Message:
        """Отправить сообщение с поддержкой embeds, компонентов, файлов"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        # Преобразовать embeds если это объекты Embed
        if embeds:
            embeds = [e.to_dict() if hasattr(e, 'to_dict') else e for e in embeds]
        
        # Преобразовать components если это объекты ActionRow
        if components:
            components = [c.to_dict() if hasattr(c, 'to_dict') else c for c in components]
        
        data = await self.http.create_message(
            channel_id, content, embeds=embeds, components=components,
            files=files, allowed_mentions=allowed_mentions,
            message_reference=message_reference, stickers=stickers,
            flags=flags, **kwargs
        )
        return Message(data, self)
    
    async def edit_message(
        self,
        channel_id: int,
        message_id: int,
        **kwargs
    ) -> Message:
        """Редактировать сообщение"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        data = await self.http.edit_message(channel_id, message_id, **kwargs)
        return Message(data, self)
    
    async def delete_message(self, channel_id: int, message_id: int):
        """Удалить сообщение"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        await self.http.delete_message(channel_id, message_id)
    
    async def wait_for(self, event: str, check=None, timeout: Optional[float] = None):
        """Ожидать событие"""
        future = asyncio.Future()
        
        def handler(*args, **kwargs):
            if check is None or check(*args, **kwargs):
                if not future.done():
                    future.set_result(args[0] if args else None)
        
        self.event(event)(handler)
        
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            # Удалить обработчик
            if event in self.event_handlers:
                self.event_handlers[event].remove(handler)
            raise
    
    # ========== Расширенные методы для работы с гильдиями ==========
    
    async def create_channel(
        self,
        guild_id: int,
        name: str,
        type: int = 0,
        **kwargs
    ) -> Channel:
        """Создать канал в гильдии"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        data = await self.http.create_channel(guild_id, name, type, **kwargs)
        guild = self.guilds.get(guild_id)
        channel = Channel(data, guild, self)
        self.channels[channel.id] = channel
        
        if self.cache:
            self.cache.set_channel(str(channel.id), data)
        
        return channel
    
    async def modify_channel(self, channel_id: int, **kwargs) -> Channel:
        """Изменить канал"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        data = await self.http.modify_channel(channel_id, **kwargs)
        channel = self.channels.get(channel_id)
        if channel:
            channel._update(data)
        else:
            guild_id = int(data.get("guild_id", 0)) if data.get("guild_id") else None
            guild = self.guilds.get(guild_id) if guild_id else None
            channel = Channel(data, guild, self)
            self.channels[channel.id] = channel
        
        if self.cache:
            self.cache.set_channel(str(channel.id), data)
        
        return channel
    
    async def delete_channel(self, channel_id: int) -> Channel:
        """Удалить канал"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        data = await self.http.delete_channel(channel_id)
        channel = self.channels.pop(channel_id, None)
        
        if self.cache:
            self.cache.channels.delete(str(channel_id))
        
        return channel
    
    async def create_role(self, guild_id: int, **kwargs) -> Role:
        """Создать роль в гильдии"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        data = await self.http.create_guild_role(guild_id, **kwargs)
        guild = self.guilds.get(guild_id)
        role = Role(data, guild, self)
        
        if guild:
            guild.roles.append(role)
        
        return role
    
    async def modify_role(self, guild_id: int, role_id: int, **kwargs) -> Role:
        """Изменить роль"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        data = await self.http.modify_guild_role(guild_id, role_id, **kwargs)
        guild = self.guilds.get(guild_id)
        role = Role(data, guild, self)
        
        if guild:
            for i, r in enumerate(guild.roles):
                if r.id == role_id:
                    guild.roles[i] = role
                    break
        
        return role
    
    async def delete_role(self, guild_id: int, role_id: int):
        """Удалить роль"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        await self.http.delete_guild_role(guild_id, role_id)
        
        guild = self.guilds.get(guild_id)
        if guild:
            guild.roles = [r for r in guild.roles if r.id != role_id]
    
    async def ban_user(self, guild_id: int, user_id: int, delete_message_days: int = 0, reason: Optional[str] = None):
        """Забанить пользователя"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        return await self.http.create_guild_ban(guild_id, user_id, delete_message_days, reason)
    
    async def unban_user(self, guild_id: int, user_id: int, reason: Optional[str] = None):
        """Разбанить пользователя"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        return await self.http.remove_guild_ban(guild_id, user_id, reason)
    
    async def kick_member(self, guild_id: int, user_id: int, reason: Optional[str] = None):
        """Исключить участника"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        return await self.http.remove_guild_member(guild_id, user_id, reason)
    
    async def add_role(self, guild_id: int, user_id: int, role_id: int):
        """Добавить роль участнику"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        return await self.http.add_guild_member_role(guild_id, user_id, role_id)
    
    async def remove_role(self, guild_id: int, user_id: int, role_id: int):
        """Удалить роль у участника"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        return await self.http.remove_guild_member_role(guild_id, user_id, role_id)
    
    async def modify_member(self, guild_id: int, user_id: int, **kwargs):
        """Изменить участника"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        return await self.http.modify_guild_member(guild_id, user_id, **kwargs)
    
    # ========== Методы для работы с webhooks ==========
    
    async def create_webhook(self, channel_id: int, name: str, avatar: Optional[str] = None, reason: Optional[str] = None) -> Dict:
        """Создать webhook"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        return await self.http.create_webhook(channel_id, name, avatar, reason)
    
    async def get_channel_webhooks(self, channel_id: int) -> List[Dict]:
        """Получить webhooks канала"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        return await self.http.get_channel_webhooks(channel_id)
    
    async def get_guild_webhooks(self, guild_id: int) -> List[Dict]:
        """Получить webhooks гильдии"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        return await self.http.get_guild_webhooks(guild_id)
    
    def get_webhook(self, webhook_id: int, webhook_token: str):
        """Получить объект Webhook"""
        from .webhook import Webhook
        return Webhook(webhook_id, webhook_token, self.http)
    
    # ========== Методы для работы с реакциями ==========
    
    async def get_reactions(
        self,
        channel_id: int,
        message_id: int,
        emoji: str,
        limit: int = 25,
        after: Optional[int] = None,
        before: Optional[int] = None
    ) -> List[Dict]:
        """Получить пользователей, поставивших реакцию"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        return await self.http.get_reactions(channel_id, message_id, emoji, limit, after, before)
    
    async def remove_all_reactions(self, channel_id: int, message_id: int):
        """Удалить все реакции с сообщения"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        return await self.http.remove_all_reactions(channel_id, message_id)
    
    async def remove_all_reactions_for_emoji(self, channel_id: int, message_id: int, emoji: str):
        """Удалить все реакции определенного эмодзи"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        return await self.http.remove_all_reactions_for_emoji(channel_id, message_id, emoji)
    
    # ========== Методы для создания гильдий ==========
    
    async def create_guild(
        self,
        name: str,
        region: Optional[str] = None,
        icon: Optional[str] = None,
        verification_level: Optional[int] = None,
        default_message_notifications: Optional[int] = None,
        explicit_content_filter: Optional[int] = None,
        roles: Optional[List[Dict]] = None,
        channels: Optional[List[Dict]] = None,
        afk_channel_id: Optional[int] = None,
        afk_timeout: Optional[int] = None,
        system_channel_id: Optional[int] = None,
        system_channel_flags: Optional[int] = None
    ) -> Guild:
        """Создать новую гильдию"""
        if not self.http:
            raise RuntimeError("HTTP client not initialized")
        
        data = await self.http.create_guild(
            name, region, icon, verification_level,
            default_message_notifications, explicit_content_filter,
            roles, channels, afk_channel_id, afk_timeout,
            system_channel_id, system_channel_flags
        )
        
        guild = Guild(data, self)
        self.guilds[guild.id] = guild
        
        if self.cache:
            self.cache.set_guild(str(guild.id), data)
        
        return guild

