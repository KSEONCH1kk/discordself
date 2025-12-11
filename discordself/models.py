"""Модели данных для Discord объектов"""

from typing import Dict, Optional, List, Any, Callable
from datetime import datetime
from .enums import ChannelType, MessageType, Status, InteractionType, InteractionResponseType


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
        # Преобразовать attachments в объекты Attachment
        attachments_data = data.get("attachments", [])
        self.attachments = [Attachment(att, client) for att in attachments_data] if attachments_data else []
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


class Interaction(BaseModel):
    """Модель Interaction (включая Modals)"""
    
    def __init__(self, data: Dict, client=None):
        super().__init__(data, client)
        self.id = int(data.get("id", 0))
        self.application_id = int(data.get("application_id", 0))
        self.type = InteractionType(data.get("type", 0))
        self.token = data.get("token", "")
        self.guild_id = int(data.get("guild_id", 0)) if data.get("guild_id") else None
        self.channel_id = int(data.get("channel_id", 0)) if data.get("channel_id") else None
        self.member = Member(data.get("member", {}), client) if data.get("member") else None
        self.user = User(data.get("user", {}), client) if data.get("user") else None
        self.data = data.get("data", {})
        self.message = Message(data.get("message", {}), client) if data.get("message") else None
        
        # Для Modal
        self.custom_id = self.data.get("custom_id", "") if self.data else ""
        self.components = self.data.get("components", []) if self.data else []
    
    @property
    def guild(self) -> Optional[Guild]:
        """Получить гильдию"""
        if self._client and self.guild_id:
            return self._client.get_guild(self.guild_id)
        return None
    
    @property
    def channel(self) -> Optional[Channel]:
        """Получить канал"""
        if self._client and self.channel_id:
            return self._client.get_channel(self.channel_id)
        return None
    
    def get_modal_value(self, custom_id: str) -> Optional[str]:
        """Получить значение поля модального окна по custom_id"""
        if self.type != InteractionType.MODAL_SUBMIT:
            return None
        
        for row in self.components:
            if row.get("type") == 1:  # ACTION_ROW
                for component in row.get("components", []):
                    if component.get("custom_id") == custom_id:
                        return component.get("value")
        return None
    
    async def respond(
        self,
        content: Optional[str] = None,
        embeds: Optional[List[Dict]] = None,
        components: Optional[List[Dict]] = None,
        ephemeral: bool = False,
        files: Optional[List] = None
    ):
        """Ответить на interaction"""
        if not self._client or not self._client.http:
            raise ValueError("Client or HTTP client not available")
        
        response_type = InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE
        data = {}
        
        if content is not None:
            data["content"] = content
        if embeds:
            data["embeds"] = embeds
        if components:
            data["components"] = components
        if ephemeral:
            data["flags"] = 64  # EPHEMERAL flag
        
        return await self._client.http.create_interaction_response(
            self.id,
            self.token,
            response_type,
            data,
            files
        )
    
    async def respond_modal(
        self,
        custom_id: str,
        title: str,
        components: List[Dict]
    ):
        """Ответить модальным окном"""
        if not self._client or not self._client.http:
            raise ValueError("Client or HTTP client not available")
        
        data = {
            "custom_id": custom_id,
            "title": title,
            "components": components
        }
        
        return await self._client.http.create_interaction_response(
            self.id,
            self.token,
            InteractionResponseType.MODAL,
            data
        )
    
    def __repr__(self) -> str:
        return f"<Interaction id={self.id} type={self.type.name}>"


class AutoModAction(BaseModel):
    """Модель действия AutoMod"""
    
    def __init__(self, data: Dict, client=None):
        super().__init__(data, client)
        self.guild_id = int(data.get("guild_id", 0))
        self.action = data.get("action", {})
        self.rule_id = int(data.get("rule_id", 0))
        self.rule_trigger_type = data.get("rule_trigger_type", 0)
        self.user_id = int(data.get("user_id", 0)) if data.get("user_id") else None
        self.channel_id = int(data.get("channel_id", 0)) if data.get("channel_id") else None
        self.message_id = int(data.get("message_id", 0)) if data.get("message_id") else None
        self.alert_system_message_id = int(data.get("alert_system_message_id", 0)) if data.get("alert_system_message_id") else None
        self.content = data.get("content", "")
        self.matched_keyword = data.get("matched_keyword")
        self.matched_content = data.get("matched_content")
    
    @property
    def guild(self) -> Optional[Guild]:
        """Получить гильдию"""
        if self._client and self.guild_id:
            return self._client.get_guild(self.guild_id)
        return None
    
    @property
    def channel(self) -> Optional[Channel]:
        """Получить канал"""
        if self._client and self.channel_id:
            return self._client.get_channel(self.channel_id)
        return None
    
    @property
    def user(self) -> Optional[User]:
        """Получить пользователя"""
        if self._client and self.user_id:
            return self._client.get_user(self.user_id)
        return None
    
    def __repr__(self) -> str:
        return f"<AutoModAction guild_id={self.guild_id} rule_id={self.rule_id}>"


class AutoModRule(BaseModel):
    """Модель правила AutoMod"""
    
    def __init__(self, data: Dict, client=None):
        super().__init__(data, client)
        self.id = int(data.get("id", 0))
        self.guild_id = int(data.get("guild_id", 0))
        self.name = data.get("name", "")
        self.creator_id = int(data.get("creator_id", 0)) if data.get("creator_id") else None
        self.event_type = data.get("event_type", 0)
        self.trigger_type = data.get("trigger_type", 0)
        self.trigger_metadata = data.get("trigger_metadata", {})
        self.actions = data.get("actions", [])
        self.enabled = data.get("enabled", True)
        self.exempt_roles = [int(r) for r in data.get("exempt_roles", [])]
        self.exempt_channels = [int(c) for c in data.get("exempt_channels", [])]
    
    @property
    def guild(self) -> Optional[Guild]:
        """Получить гильдию"""
        if self._client and self.guild_id:
            return self._client.get_guild(self.guild_id)
        return None
    
    def __repr__(self) -> str:
        return f"<AutoModRule id={self.id} name={self.name}>"


class Attachment(BaseModel):
    """Модель вложения (Attachment)"""
    
    def __init__(self, data: Dict, client=None):
        super().__init__(data, client)
        self.id = int(data.get("id", 0))
        self.filename = data.get("filename", "")
        self.description = data.get("description")
        self.content_type = data.get("content_type")
        self.size = data.get("size", 0)
        self.url = data.get("url", "")
        self.proxy_url = data.get("proxy_url", "")
        self.height = data.get("height")
        self.width = data.get("width")
        self.ephemeral = data.get("ephemeral", False)
        self.duration_seconds = data.get("duration_seconds")
        self.waveform = data.get("waveform")
    
    @property
    def is_image(self) -> bool:
        """Проверить, является ли вложение изображением"""
        return self.content_type and self.content_type.startswith("image/")
    
    @property
    def is_video(self) -> bool:
        """Проверить, является ли вложение видео"""
        return self.content_type and self.content_type.startswith("video/")
    
    @property
    def is_audio(self) -> bool:
        """Проверить, является ли вложение аудио"""
        return self.content_type and self.content_type.startswith("audio/")
    
    def __repr__(self) -> str:
        return f"<Attachment id={self.id} filename={self.filename} size={self.size}>"


class Invite(BaseModel):
    """Модель приглашения (Invite)"""
    
    def __init__(self, data: Dict, client=None):
        super().__init__(data, client)
        self.code = data.get("code", "")
        self.guild_id = int(data.get("guild_id", 0)) if data.get("guild_id") else None
        self.guild = Guild(data.get("guild", {}), client) if data.get("guild") else None
        self.channel_id = int(data.get("channel_id", 0)) if data.get("channel_id") else None
        self.channel = Channel(data.get("channel", {}), client) if data.get("channel") else None
        self.inviter = User(data.get("inviter", {}), client) if data.get("inviter") else None
        self.target_type = data.get("target_type")
        self.target_user = User(data.get("target_user", {}), client) if data.get("target_user") else None
        self.target_application = data.get("target_application")
        self.approximate_presence_count = data.get("approximate_presence_count")
        self.approximate_member_count = data.get("approximate_member_count")
        self.expires_at = data.get("expires_at")
        self.stage_instance = data.get("stage_instance")
        self.guild_scheduled_event = data.get("guild_scheduled_event")
        self.uses = data.get("uses", 0)
        self.max_uses = data.get("max_uses", 0)
        self.max_age = data.get("max_age", 0)
        self.temporary = data.get("temporary", False)
        self.created_at = data.get("created_at")
    
    @property
    def url(self) -> str:
        """Получить URL приглашения"""
        return f"https://discord.gg/{self.code}"
    
    def __repr__(self) -> str:
        return f"<Invite code={self.code} guild_id={self.guild_id}>"


class Integration(BaseModel):
    """Модель интеграции (Integration)"""
    
    def __init__(self, data: Dict, client=None):
        super().__init__(data, client)
        self.id = int(data.get("id", 0))
        self.name = data.get("name", "")
        self.type = data.get("type", "")
        self.enabled = data.get("enabled", False)
        self.syncing = data.get("syncing", False)
        self.role_id = int(data.get("role_id", 0)) if data.get("role_id") else None
        self.enable_emoticons = data.get("enable_emoticons", False)
        self.expire_behavior = data.get("expire_behavior", 0)
        self.expire_grace_period = data.get("expire_grace_period", 0)
        self.user = User(data.get("user", {}), client) if data.get("user") else None
        self.account = data.get("account", {})
        self.synced_at = data.get("synced_at")
        self.subscriber_count = data.get("subscriber_count", 0)
        self.revoked = data.get("revoked", False)
        self.application = data.get("application", {})
        self.scopes = data.get("scopes", [])
    
    @property
    def guild(self) -> Optional[Guild]:
        """Получить гильдию"""
        # Integration обычно привязана к гильдии через client
        return None
    
    def __repr__(self) -> str:
        return f"<Integration id={self.id} name={self.name} type={self.type}>"


class StageInstance(BaseModel):
    """Модель Stage Instance"""
    
    def __init__(self, data: Dict, client=None):
        super().__init__(data, client)
        self.id = int(data.get("id", 0))
        self.guild_id = int(data.get("guild_id", 0))
        self.channel_id = int(data.get("channel_id", 0))
        self.topic = data.get("topic", "")
        self.privacy_level = data.get("privacy_level", 1)
        self.discoverable_disabled = data.get("discoverable_disabled", False)
        self.guild_scheduled_event_id = int(data.get("guild_scheduled_event_id", 0)) if data.get("guild_scheduled_event_id") else None
    
    @property
    def guild(self) -> Optional[Guild]:
        """Получить гильдию"""
        if self._client and self.guild_id:
            return self._client.get_guild(self.guild_id)
        return None
    
    @property
    def channel(self) -> Optional[Channel]:
        """Получить канал"""
        if self._client and self.channel_id:
            return self._client.get_channel(self.channel_id)
        return None
    
    def __repr__(self) -> str:
        return f"<StageInstance id={self.id} topic={self.topic}>"


class ScheduledEvent(BaseModel):
    """Модель Scheduled Event"""
    
    def __init__(self, data: Dict, client=None):
        super().__init__(data, client)
        self.id = int(data.get("id", 0))
        self.guild_id = int(data.get("guild_id", 0))
        self.channel_id = int(data.get("channel_id", 0)) if data.get("channel_id") else None
        self.creator_id = int(data.get("creator_id", 0)) if data.get("creator_id") else None
        self.name = data.get("name", "")
        self.description = data.get("description")
        self.scheduled_start_time = data.get("scheduled_start_time")
        self.scheduled_end_time = data.get("scheduled_end_time")
        self.privacy_level = data.get("privacy_level", 2)
        self.status = data.get("status", 1)
        self.entity_type = data.get("entity_type", 0)
        self.entity_id = int(data.get("entity_id", 0)) if data.get("entity_id") else None
        self.entity_metadata = data.get("entity_metadata", {})
        self.creator = User(data.get("creator", {}), client) if data.get("creator") else None
        self.user_count = data.get("user_count", 0)
        self.image = data.get("image")
    
    @property
    def guild(self) -> Optional[Guild]:
        """Получить гильдию"""
        if self._client and self.guild_id:
            return self._client.get_guild(self.guild_id)
        return None
    
    @property
    def channel(self) -> Optional[Channel]:
        """Получить канал"""
        if self._client and self.channel_id:
            return self._client.get_channel(self.channel_id)
        return None
    
    def __repr__(self) -> str:
        return f"<ScheduledEvent id={self.id} name={self.name}>"

