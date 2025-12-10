"""Модели данных для Discord объектов"""

from typing import Dict, Optional, List, Any, Callable
from datetime import datetime
from .enums import ChannelType, MessageType, Status


class BaseModel:
    """Базовый класс для всех моделей"""
    
    def __init__(self, data: Dict, client=None):
        self._client = client
        self._update(data)
    
    def _update(self, data: Dict):
        """Обновить данные модели"""
        for key, value in data.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class User(BaseModel):
    """Модель пользователя Discord"""
    
    def __init__(self, data: Dict[str, Any], client: Optional['Client'] = None) -> None:
        super().__init__(data, client)
        self.id = int(data.get("id", 0))
        self.username = data.get("username", "")
        self.discriminator = data.get("discriminator", "0")
        self.global_name = data.get("global_name")
        self.avatar = data.get("avatar")
        self.bot = data.get("bot", False)
        self.system = data.get("system", False)
        self.mfa_enabled = data.get("mfa_enabled", False)
        self.banner = data.get("banner")
        self.accent_color = data.get("accent_color")
        self.locale = data.get("locale")
        self.verified = data.get("verified", False)
        self.email = data.get("email")
        self.flags = data.get("flags", 0)
        self.premium_type = data.get("premium_type", 0)
        self.public_flags = data.get("public_flags", 0)
    
    @property
    def mention(self) -> str:
        """Упоминание пользователя"""
        return f"<@{self.id}>"
    
    @property
    def display_name(self) -> str:
        """Отображаемое имя"""
        return self.global_name or self.username
    
    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"


class Member(BaseModel):
    """Модель участника гильдии"""
    
    def __init__(self, data: Dict, guild=None, client=None):
        super().__init__(data, client)
        self.guild = guild
        self.user = User(data.get("user", {}), client) if data.get("user") else None
        self.nick = data.get("nick")
        self.avatar = data.get("avatar")
        self.roles = [int(r) for r in data.get("roles", [])]
        self.joined_at = data.get("joined_at")
        self.premium_since = data.get("premium_since")
        self.deaf = data.get("deaf", False)
        self.mute = data.get("mute", False)
        self.flags = data.get("flags", 0)
        self.pending = data.get("pending", False)
        self.permissions = data.get("permissions")
        self.communication_disabled_until = data.get("communication_disabled_until")
    
    @property
    def display_name(self) -> str:
        """Отображаемое имя"""
        return self.nick or (self.user.display_name if self.user else "Unknown")
    
    def __repr__(self):
        return f"<Member user={self.user} guild={self.guild}>"


class Role(BaseModel):
    """Модель роли"""
    
    def __init__(self, data: Dict, guild=None, client=None):
        super().__init__(data, client)
        self.guild = guild
        self.id = int(data.get("id", 0))
        self.name = data.get("name", "")
        self.color = data.get("color", 0)
        self.hoist = data.get("hoist", False)
        self.icon = data.get("icon")
        self.unicode_emoji = data.get("unicode_emoji")
        self.position = data.get("position", 0)
        self.permissions = data.get("permissions", "0")
        self.managed = data.get("managed", False)
        self.mentionable = data.get("mentionable", False)
        self.tags = data.get("tags")
    
    @property
    def mention(self) -> str:
        """Упоминание роли"""
        return f"<@&{self.id}>"
    
    def __repr__(self):
        return f"<Role id={self.id} name={self.name}>"


class Emoji(BaseModel):
    """Модель эмодзи"""
    
    def __init__(self, data: Dict, guild=None, client=None):
        super().__init__(data, client)
        self.guild = guild
        self.id = int(data.get("id", 0)) if data.get("id") else None
        self.name = data.get("name", "")
        self.roles = [int(r) for r in data.get("roles", [])]
        self.user = User(data.get("user", {}), client) if data.get("user") else None
        self.require_colons = data.get("require_colons", False)
        self.managed = data.get("managed", False)
        self.animated = data.get("animated", False)
        self.available = data.get("available", True)
    
    @property
    def mention(self) -> str:
        """Упоминание эмодзи"""
        if self.animated:
            return f"<a:{self.name}:{self.id}>"
        return f"<:{self.name}:{self.id}>"
    
    def __repr__(self):
        return f"<Emoji id={self.id} name={self.name}>"


class Channel(BaseModel):
    """Модель канала"""
    
    def __init__(self, data: Dict, guild=None, client=None):
        super().__init__(data, client)
        self.guild = guild
        self.id = int(data.get("id", 0))
        self.type = ChannelType(data.get("type", 0))
        self.name = data.get("name")
        self.topic = data.get("topic")
        self.bitrate = data.get("bitrate")
        self.user_limit = data.get("user_limit")
        self.rate_limit_per_user = data.get("rate_limit_per_user")
        self.position = data.get("position")
        self.permission_overwrites = data.get("permission_overwrites", [])
        self.parent_id = int(data.get("parent_id", 0)) if data.get("parent_id") else None
        self.nsfw = data.get("nsfw", False)
        self.last_message_id = int(data.get("last_message_id", 0)) if data.get("last_message_id") else None
    
    @property
    def mention(self) -> str:
        """Упоминание канала"""
        return f"<#{self.id}>"
    
    async def send(
        self,
        content: Optional[str] = None,
        embeds: Optional[list] = None,
        components: Optional[list] = None,
        files: Optional[list] = None,
        allowed_mentions: Optional[Dict] = None,
        message_reference: Optional[Dict] = None,
        stickers: Optional[list] = None,
        flags: Optional[int] = None,
        **kwargs
    ):
        """Отправить сообщение в канал с поддержкой embeds, компонентов, файлов"""
        if self._client:
            # Преобразовать embeds если это объекты Embed
            if embeds:
                embeds = [e.to_dict() if hasattr(e, 'to_dict') else e for e in embeds]
            
            # Преобразовать components если это объекты ActionRow
            if components:
                components = [c.to_dict() if hasattr(c, 'to_dict') else c for c in components]
            
            data = await self._client.http.create_message(
                self.id, content, embeds=embeds, components=components,
                files=files, allowed_mentions=allowed_mentions,
                message_reference=message_reference, stickers=stickers,
                flags=flags, **kwargs
            )
            return Message(data, self._client)
    
    async def fetch_messages(
        self,
        limit: int = 50,
        before: Optional[int] = None,
        after: Optional[int] = None,
        around: Optional[int] = None
    ):
        """Получить сообщения канала"""
        if self._client:
            data = await self._client.http.get_channel_messages(self.id, limit, before, after, around)
            return [Message(msg, self._client) for msg in data]
    
    async def fetch_all_messages(
        self,
        limit: Optional[int] = None,
        before: Optional[int] = None,
        after: Optional[int] = None,
        check: Optional[Callable] = None
    ):
        """Получить все сообщения канала с пагинацией"""
        if self._client:
            data = await self._client.http.get_all_channel_messages(self.id, limit, before, after, check)
            return [Message(msg, self._client) for msg in data]
    
    def __repr__(self):
        return f"<Channel id={self.id} name={self.name} type={self.type.name}>"


class Message(BaseModel):
    """Модель сообщения"""
    
    def __init__(self, data: Dict, client=None):
        super().__init__(data, client)
        self.id = int(data.get("id", 0))
        self.channel_id = int(data.get("channel_id", 0))
        self.author = User(data.get("author", {}), client) if data.get("author") else None
        self.content = data.get("content", "")
        self.timestamp = data.get("timestamp")
        self.edited_timestamp = data.get("edited_timestamp")
        self.tts = data.get("tts", False)
        self.mention_everyone = data.get("mention_everyone", False)
        self.mentions = [User(m, client) for m in data.get("mentions", [])]
        self.mention_roles = [int(r) for r in data.get("mention_roles", [])]
        self.attachments = data.get("attachments", [])
        self.embeds = data.get("embeds", [])
        self.reactions = data.get("reactions", [])
        self.nonce = data.get("nonce")
        self.pinned = data.get("pinned", False)
        self.type = MessageType(data.get("type", 0))
        self.activity = data.get("activity")
        self.application = data.get("application")
        self.application_id = int(data.get("application_id", 0)) if data.get("application_id") else None
        self.message_reference = data.get("message_reference")
        self.flags = data.get("flags", 0)
        self.referenced_message = None
        if data.get("referenced_message"):
            self.referenced_message = Message(data["referenced_message"], client)
        self.interaction = data.get("interaction")
        self.thread = data.get("thread")
        self.components = data.get("components", [])
        self.sticker_items = data.get("sticker_items", [])
        self.stickers = data.get("stickers", [])
    
    @property
    def channel(self):
        """Получить канал сообщения"""
        if not self._client:
            return None
        
        # Попытаться получить канал из кэша
        channel = self._client.get_channel(self.channel_id)
        
        # Если канал не найден в кэше, создать минимальный объект канала
        # Это позволяет отправлять сообщения даже если полные данные канала не закэшированы
        if channel is None and self.channel_id:
            # Создать минимальный объект канала с только ID
            # Это достаточно для отправки сообщений
            channel_data = {"id": self.channel_id, "type": 0}  # type 0 = GUILD_TEXT (по умолчанию)
            channel = Channel(channel_data, None, self._client)
            # Не добавляем в кэш, так как это временный объект
            # Полные данные будут загружены асинхронно через _ensure_channel_cached
        
        return channel
    
    @property
    def guild(self):
        """Получить гильдию сообщения"""
        if self.channel:
            return self.channel.guild
        return None
    
    async def edit(
        self,
        content: Optional[str] = None,
        embeds: Optional[list] = None,
        components: Optional[list] = None,
        files: Optional[list] = None,
        allowed_mentions: Optional[Dict] = None,
        **kwargs
    ):
        """Редактировать сообщение"""
        if self._client:
            # Преобразовать embeds если это объекты Embed
            if embeds:
                embeds = [e.to_dict() if hasattr(e, 'to_dict') else e for e in embeds]
            
            # Преобразовать components если это объекты ActionRow
            if components:
                components = [c.to_dict() if hasattr(c, 'to_dict') else c for c in components]
            
            data = await self._client.http.edit_message(
                self.channel_id, self.id,
                content=content, embeds=embeds, components=components,
                files=files, allowed_mentions=allowed_mentions, **kwargs
            )
            if data:
                self._update(data)
                return Message(data, self._client)
            return self
    
    async def delete(self):
        """Удалить сообщение"""
        if self._client:
            return await self._client.http.delete_message(self.channel_id, self.id)
    
    async def add_reaction(self, emoji: str):
        """Добавить реакцию"""
        if self._client:
            return await self._client.http.add_reaction(self.channel_id, self.id, emoji)
    
    async def remove_reaction(self, emoji: str):
        """Удалить реакцию"""
        if self._client:
            return await self._client.http.remove_reaction(self.channel_id, self.id, emoji)
    
    def __repr__(self):
        return f"<Message id={self.id} author={self.author} content={self.content[:50]}>"


class Guild(BaseModel):
    """Модель гильдии (сервера)"""
    
    def __init__(self, data: Dict, client=None):
        super().__init__(data, client)
        self.id = int(data.get("id", 0))
        self.name = data.get("name", "")
        self.icon = data.get("icon")
        self.icon_hash = data.get("icon_hash")
        self.splash = data.get("splash")
        self.discovery_splash = data.get("discovery_splash")
        self.owner_id = int(data.get("owner_id", 0)) if data.get("owner_id") else None
        self.owner = data.get("owner", False)
        self.permissions = data.get("permissions")
        self.region = data.get("region")
        self.afk_channel_id = int(data.get("afk_channel_id", 0)) if data.get("afk_channel_id") else None
        self.afk_timeout = data.get("afk_timeout", 0)
        self.widget_enabled = data.get("widget_enabled", False)
        self.widget_channel_id = int(data.get("widget_channel_id", 0)) if data.get("widget_channel_id") else None
        self.verification_level = data.get("verification_level", 0)
        self.default_message_notifications = data.get("default_message_notifications", 0)
        self.explicit_content_filter = data.get("explicit_content_filter", 0)
        self.roles = [Role(r, self, client) for r in data.get("roles", [])]
        self.emojis = [Emoji(e, self, client) for e in data.get("emojis", [])]
        self.features = data.get("features", [])
        self.mfa_level = data.get("mfa_level", 0)
        self.application_id = int(data.get("application_id", 0)) if data.get("application_id") else None
        self.system_channel_id = int(data.get("system_channel_id", 0)) if data.get("system_channel_id") else None
        self.system_channel_flags = data.get("system_channel_flags", 0)
        self.rules_channel_id = int(data.get("rules_channel_id", 0)) if data.get("rules_channel_id") else None
        self.max_presences = data.get("max_presences")
        self.max_members = data.get("max_members")
        self.vanity_url_code = data.get("vanity_url_code")
        self.description = data.get("description")
        self.banner = data.get("banner")
        self.premium_tier = data.get("premium_tier", 0)
        self.premium_subscription_count = data.get("premium_subscription_count", 0)
        self.preferred_locale = data.get("preferred_locale", "en-US")
        self.public_updates_channel_id = int(data.get("public_updates_channel_id", 0)) if data.get("public_updates_channel_id") else None
        self.max_video_channel_users = data.get("max_video_channel_users", 0)
        self.approximate_member_count = data.get("approximate_member_count")
        self.approximate_presence_count = data.get("approximate_presence_count")
        self.welcome_screen = data.get("welcome_screen")
        self.nsfw_level = data.get("nsfw_level", 0)
        self.stickers = data.get("stickers", [])
        self.premium_progress_bar_enabled = data.get("premium_progress_bar_enabled", False)
    
    async def fetch_channels(self):
        """Получить каналы гильдии"""
        if self._client:
            return await self._client.http.get_guild_channels(self.id)
    
    async def fetch_members(self, limit: int = 1, after: Optional[int] = None):
        """Получить участников гильдии"""
        if self._client:
            return await self._client.http.get_guild_members(self.id, limit, after)
    
    def get_channel(self, channel_id: int):
        """Получить канал гильдии"""
        if self._client:
            return self._client.get_channel(channel_id)
        return None
    
    def __repr__(self):
        return f"<Guild id={self.id} name={self.name}>"


class VoiceState(BaseModel):
    """Модель состояния голосового подключения"""
    
    def __init__(self, data: Dict[str, Any], guild: Optional[Guild] = None, client: Optional['Client'] = None) -> None:
        super().__init__(data, client)
        self.guild = guild
        self.channel_id = int(data.get("channel_id", 0)) if data.get("channel_id") else None
        self.user_id = int(data.get("user_id", 0))
        self.session_id = data.get("session_id")
        self.deaf = data.get("deaf", False)
        self.mute = data.get("mute", False)
        self.self_deaf = data.get("self_deaf", False)
        self.self_mute = data.get("self_mute", False)
        self.self_stream = data.get("self_stream", False)
        self.self_video = data.get("self_video", False)
        self.suppress = data.get("suppress", False)
        self.request_to_speak_timestamp = data.get("request_to_speak_timestamp")
    
    @property
    def channel(self) -> Optional[Channel]:
        """Получить канал"""
        if self._client and self.channel_id:
            return self._client.get_channel(self.channel_id)
        return None
    
    @property
    def user(self) -> Optional[User]:
        """Получить пользователя"""
        if self._client:
            return self._client.get_user(self.user_id)
        return None
    
    def __repr__(self) -> str:
        return f"<VoiceState user_id={self.user_id} channel_id={self.channel_id}>"

