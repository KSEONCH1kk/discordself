"""HTTP клиент для Discord REST API"""

import aiohttp
import json
import logging
import asyncio
from typing import Dict, Optional, Any, Union, List, Callable
from .exceptions import HTTPException, RateLimitException
from .ratelimit import RateLimiter

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP клиент для взаимодействия с Discord API"""
    
    BASE_URL = "https://discord.com/api/v10"
    
    def __init__(self, token: str, user_agent: str = "DiscordSelf/1.0.0"):
        self.token = token
        self.user_agent = user_agent
        self.session: Optional[aiohttp.ClientSession] = None
        self.ratelimiter = RateLimiter()
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def start(self):
        """Инициализировать HTTP сессию"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Закрыть HTTP сессию"""
        if self.session:
            try:
                await self.session.close()
                # Дать время на закрытие всех соединений
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error closing HTTP session: {e}")
            finally:
                self.session = None
    
    def _get_headers(self, **kwargs) -> Dict[str, str]:
        """Получить заголовки для запроса"""
        headers = {
            "Authorization": self.token,
            "User-Agent": self.user_agent,
            "Content-Type": "application/json",
        }
        headers.update(kwargs)
        return headers
    
    async def request(
        self,
        method: str,
        route: str,
        **kwargs
    ) -> Union[Dict, list, None]:
        """Выполнить HTTP запрос"""
        if not self.session:
            await self.start()
        
        # Получить разрешение от rate limiter
        await self.ratelimiter.acquire(route, method)
        
        url = f"{self.BASE_URL}{route}"
        headers = self._get_headers(**kwargs.pop("headers", {}))
        
        # Сериализация JSON если нужно
        if "json" in kwargs:
            kwargs["data"] = json.dumps(kwargs.pop("json"))
        
        try:
            async with self.session.request(method, url, headers=headers, **kwargs) as response:
                # Обновить rate limit информацию
                self.ratelimiter.update_ratelimit(route, method, response.headers)
                
                # Проверка на rate limit
                if response.status == 429:
                    retry_after = float(response.headers.get("Retry-After", 1))
                    raise RateLimitException(retry_after)
                
                # Обработка ответа
                if response.status == 204:
                    return None
                
                try:
                    data = await response.json()
                except:
                    data = await response.text()
                
                if response.status >= 400:
                    raise HTTPException(response, data)
                
                return data
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise HTTPException(None, str(e))
    
    # Методы для различных эндпоинтов
    
    async def get_current_user(self) -> Dict:
        """Получить текущего пользователя"""
        return await self.request("GET", "/users/@me")
    
    async def get_user(self, user_id: int) -> Dict:
        """Получить пользователя по ID"""
        return await self.request("GET", f"/users/{user_id}")
    
    async def modify_current_user(self, **kwargs) -> Dict:
        """Изменить текущего пользователя"""
        return await self.request("PATCH", "/users/@me", json=kwargs)
    
    async def get_guilds(self, limit: int = 200, before: Optional[int] = None, after: Optional[int] = None) -> list:
        """Получить список гильдий"""
        params = {"limit": limit}
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return await self.request("GET", "/users/@me/guilds", params=params)
    
    async def get_guild(self, guild_id: int) -> Dict:
        """Получить гильдию"""
        return await self.request("GET", f"/guilds/{guild_id}")
    
    async def get_guild_channels(self, guild_id: int) -> list:
        """Получить каналы гильдии"""
        return await self.request("GET", f"/guilds/{guild_id}/channels")
    
    async def get_channel(self, channel_id: int) -> Dict:
        """Получить канал"""
        return await self.request("GET", f"/channels/{channel_id}")
    
    async def get_channel_messages(
        self,
        channel_id: int,
        limit: int = 50,
        before: Optional[int] = None,
        after: Optional[int] = None,
        around: Optional[int] = None
    ) -> list:
        """Получить сообщения канала"""
        params = {"limit": min(limit, 100)}  # Максимум 100
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        if around:
            params["around"] = around
        return await self.request("GET", f"/channels/{channel_id}/messages", params=params)
    
    async def get_all_channel_messages(
        self,
        channel_id: int,
        limit: Optional[int] = None,
        before: Optional[int] = None,
        after: Optional[int] = None,
        check: Optional[Callable] = None
    ) -> list:
        """Получить все сообщения канала с пагинацией"""
        all_messages = []
        last_id = before
        
        while True:
            batch = await self.get_channel_messages(
                channel_id,
                limit=100,
                before=last_id,
                after=after
            )
            
            if not batch:
                break
            
            for msg in batch:
                if check is None or check(msg):
                    all_messages.append(msg)
            
            if len(batch) < 100:
                break
            
            last_id = int(batch[-1]["id"])
            
            if limit and len(all_messages) >= limit:
                break
            
            # Небольшая задержка для избежания rate limit
            await asyncio.sleep(0.5)
        
        return all_messages[:limit] if limit else all_messages
    
    async def search_messages(
        self,
        channel_id: Optional[int] = None,
        guild_id: Optional[int] = None,
        author_id: Optional[int] = None,
        mentions: Optional[int] = None,
        has: Optional[str] = None,
        min_id: Optional[int] = None,
        max_id: Optional[int] = None,
        limit: int = 25,
        offset: int = 0
    ) -> Dict:
        """Поиск сообщений (только для гильдий)"""
        if not guild_id:
            raise ValueError("guild_id is required for search")
        
        params = {
            "limit": min(limit, 25),
            "offset": offset
        }
        
        if channel_id:
            params["channel_id"] = channel_id
        if author_id:
            params["author_id"] = author_id
        if mentions:
            params["mentions"] = mentions
        if has:
            params["has"] = has
        if min_id:
            params["min_id"] = min_id
        if max_id:
            params["max_id"] = max_id
        
        return await self.request("GET", f"/guilds/{guild_id}/messages/search", params=params)
    
    async def get_message(self, channel_id: int, message_id: int) -> Dict:
        """Получить сообщение"""
        return await self.request("GET", f"/channels/{channel_id}/messages/{message_id}")
    
    async def create_message(
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
    ) -> Dict:
        """Создать сообщение с поддержкой embeds, компонентов, файлов и т.д."""
        # Если есть файлы, используем multipart/form-data
        if files:
            return await self._create_message_with_files(
                channel_id, content, embeds, components, files,
                allowed_mentions, message_reference, stickers, flags, **kwargs
            )
        
        # Обычный JSON запрос
        data = {}
        if content:
            data["content"] = content
        if embeds:
            data["embeds"] = embeds
        if components:
            data["components"] = components
        if allowed_mentions:
            data["allowed_mentions"] = allowed_mentions
        if message_reference:
            data["message_reference"] = message_reference
        if stickers:
            data["sticker_ids"] = stickers
        if flags is not None:
            data["flags"] = flags
        data.update(kwargs)
        
        # Discord требует, чтобы было либо content, либо embeds, либо files
        # Проверяем перед добавлением fallback
        has_content = bool(data.get("content"))
        has_embeds = bool(data.get("embeds"))
        if not has_content and not has_embeds and not files:
            # Если есть embeds, но они пустые, добавим content
            if embeds and len(embeds) == 0:
                data["content"] = "\u200b"
            elif not embeds:
                data["content"] = "\u200b"
        
        return await self.request("POST", f"/channels/{channel_id}/messages", json=data)
    
    async def _create_message_with_files(
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
    ) -> Dict:
        """Создать сообщение с файлами (multipart/form-data)"""
        if not self.session:
            await self.start()
        
        await self.ratelimiter.acquire(f"/channels/{channel_id}/messages", "POST")
        
        url = f"{self.BASE_URL}/channels/{channel_id}/messages"
        headers = {
            "Authorization": self.token,
            "User-Agent": self.user_agent,
        }
        
        form_data = aiohttp.FormData()
        
        payload = {}
        if content:
            payload["content"] = content
        if embeds:
            payload["embeds"] = embeds
        if components:
            payload["components"] = components
        if allowed_mentions:
            payload["allowed_mentions"] = allowed_mentions
        if message_reference:
            payload["message_reference"] = message_reference
        if stickers:
            payload["sticker_ids"] = stickers
        if flags is not None:
            payload["flags"] = flags
        payload.update(kwargs)
        
        form_data.add_field("payload_json", json.dumps(payload), content_type="application/json")
        
        # Добавить файлы
        for i, file_data in enumerate(files):
            if isinstance(file_data, dict):
                filename = file_data.get("filename", f"file{i}.png")
                file_obj = file_data.get("file")
                content_type = file_data.get("content_type", "application/octet-stream")
                form_data.add_field(f"files[{i}]", file_obj, filename=filename, content_type=content_type)
            else:
                form_data.add_field(f"files[{i}]", file_data, filename=f"file{i}.png")
        
        try:
            async with self.session.post(url, headers=headers, data=form_data) as response:
                self.ratelimiter.update_ratelimit(f"/channels/{channel_id}/messages", "POST", response.headers)
                
                if response.status == 429:
                    retry_after = float(response.headers.get("Retry-After", 1))
                    raise RateLimitException(retry_after)
                
                if response.status == 204:
                    return None
                
                try:
                    data = await response.json()
                except:
                    data = await response.text()
                
                if response.status >= 400:
                    raise HTTPException(response, data)
                
                return data
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise HTTPException(None, str(e))
    
    async def edit_message(
        self,
        channel_id: int,
        message_id: int,
        **kwargs
    ) -> Dict:
        """Редактировать сообщение"""
        return await self.request("PATCH", f"/channels/{channel_id}/messages/{message_id}", json=kwargs)
    
    async def delete_message(self, channel_id: int, message_id: int):
        """Удалить сообщение"""
        return await self.request("DELETE", f"/channels/{channel_id}/messages/{message_id}")
    
    async def bulk_delete_messages(self, channel_id: int, message_ids: list):
        """Массовое удаление сообщений"""
        return await self.request("POST", f"/channels/{channel_id}/messages/bulk-delete", json={"messages": message_ids})
    
    async def add_reaction(self, channel_id: int, message_id: int, emoji: str):
        """Добавить реакцию"""
        emoji = emoji.replace(":", "%3A") if ":" in emoji else emoji
        return await self.request("PUT", f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me")
    
    async def remove_reaction(self, channel_id: int, message_id: int, emoji: str):
        """Удалить реакцию"""
        emoji = emoji.replace(":", "%3A") if ":" in emoji else emoji
        return await self.request("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me")
    
    async def get_guild_members(self, guild_id: int, limit: int = 1, after: Optional[int] = None) -> list:
        """Получить участников гильдии"""
        params = {"limit": limit}
        if after:
            params["after"] = after
        return await self.request("GET", f"/guilds/{guild_id}/members", params=params)
    
    async def get_guild_member(self, guild_id: int, user_id: int) -> Dict:
        """Получить участника гильдии"""
        return await self.request("GET", f"/guilds/{guild_id}/members/{user_id}")
    
    async def modify_guild_member(self, guild_id: int, user_id: int, **kwargs):
        """Изменить участника гильдии"""
        return await self.request("PATCH", f"/guilds/{guild_id}/members/{user_id}", json=kwargs)
    
    async def add_guild_member_role(self, guild_id: int, user_id: int, role_id: int):
        """Добавить роль участнику"""
        return await self.request("PUT", f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}")
    
    async def remove_guild_member_role(self, guild_id: int, user_id: int, role_id: int):
        """Удалить роль у участника"""
        return await self.request("DELETE", f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}")
    
    async def get_guild_roles(self, guild_id: int) -> list:
        """Получить роли гильдии"""
        return await self.request("GET", f"/guilds/{guild_id}/roles")
    
    async def create_guild_role(self, guild_id: int, **kwargs) -> Dict:
        """Создать роль в гильдии"""
        return await self.request("POST", f"/guilds/{guild_id}/roles", json=kwargs)
    
    async def modify_guild_role(self, guild_id: int, role_id: int, **kwargs) -> Dict:
        """Изменить роль гильдии"""
        return await self.request("PATCH", f"/guilds/{guild_id}/roles/{role_id}", json=kwargs)
    
    async def delete_guild_role(self, guild_id: int, role_id: int):
        """Удалить роль гильдии"""
        return await self.request("DELETE", f"/guilds/{guild_id}/roles/{role_id}")
    
    async def trigger_typing(self, channel_id: int):
        """Отправить индикатор печати"""
        return await self.request("POST", f"/channels/{channel_id}/typing")
    
    async def create_dm(self, recipient_id: int) -> Dict:
        """Создать DM канал"""
        return await self.request("POST", "/users/@me/channels", json={"recipient_id": recipient_id})
    
    async def create_guild(
        self,
        name: str,
        region: Optional[str] = None,
        icon: Optional[str] = None,
        verification_level: Optional[int] = None,
        default_message_notifications: Optional[int] = None,
        explicit_content_filter: Optional[int] = None,
        roles: Optional[list] = None,
        channels: Optional[list] = None,
        afk_channel_id: Optional[int] = None,
        afk_timeout: Optional[int] = None,
        system_channel_id: Optional[int] = None,
        system_channel_flags: Optional[int] = None
    ) -> Dict:
        """Создать новую гильдию"""
        data = {"name": name}
        if region:
            data["region"] = region
        if icon:
            data["icon"] = icon
        if verification_level is not None:
            data["verification_level"] = verification_level
        if default_message_notifications is not None:
            data["default_message_notifications"] = default_message_notifications
        if explicit_content_filter is not None:
            data["explicit_content_filter"] = explicit_content_filter
        if roles:
            data["roles"] = roles
        if channels:
            data["channels"] = channels
        if afk_channel_id:
            data["afk_channel_id"] = afk_channel_id
        if afk_timeout:
            data["afk_timeout"] = afk_timeout
        if system_channel_id:
            data["system_channel_id"] = system_channel_id
        if system_channel_flags is not None:
            data["system_channel_flags"] = system_channel_flags
        return await self.request("POST", "/guilds", json=data)
    
    async def get_gateway(self) -> Dict:
        """Получить Gateway URL"""
        return await self.request("GET", "/gateway")
    
    async def get_gateway_bot(self) -> Dict:
        """Получить Gateway URL с информацией о боте"""
        return await self.request("GET", "/gateway/bot")
    
    # ========== Расширенные методы для реакций ==========
    
    async def get_reactions(
        self,
        channel_id: int,
        message_id: int,
        emoji: str,
        limit: int = 25,
        after: Optional[int] = None,
        before: Optional[int] = None
    ) -> list:
        """Получить пользователей, поставивших реакцию"""
        emoji = emoji.replace(":", "%3A") if ":" in emoji else emoji
        params = {"limit": min(limit, 100)}
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        return await self.request("GET", f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}", params=params)
    
    async def remove_all_reactions(self, channel_id: int, message_id: int):
        """Удалить все реакции с сообщения"""
        return await self.request("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions")
    
    async def remove_all_reactions_for_emoji(self, channel_id: int, message_id: int, emoji: str):
        """Удалить все реакции определенного эмодзи"""
        emoji = emoji.replace(":", "%3A") if ":" in emoji else emoji
        return await self.request("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}")
    
    async def remove_user_reaction(self, channel_id: int, message_id: int, emoji: str, user_id: int):
        """Удалить реакцию пользователя"""
        emoji = emoji.replace(":", "%3A") if ":" in emoji else emoji
        return await self.request("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}")
    
    # ========== Методы для работы с каналами ==========
    
    async def create_channel(
        self,
        guild_id: int,
        name: str,
        type: int = 0,
        topic: Optional[str] = None,
        bitrate: Optional[int] = None,
        user_limit: Optional[int] = None,
        rate_limit_per_user: Optional[int] = None,
        position: Optional[int] = None,
        permission_overwrites: Optional[list] = None,
        parent_id: Optional[int] = None,
        nsfw: Optional[bool] = None
    ) -> Dict:
        """Создать канал в гильдии"""
        data = {"name": name, "type": type}
        if topic:
            data["topic"] = topic
        if bitrate:
            data["bitrate"] = bitrate
        if user_limit:
            data["user_limit"] = user_limit
        if rate_limit_per_user:
            data["rate_limit_per_user"] = rate_limit_per_user
        if position is not None:
            data["position"] = position
        if permission_overwrites:
            # Убедиться, что permission_overwrites в правильном формате
            data["permission_overwrites"] = permission_overwrites
        if parent_id:
            data["parent_id"] = str(parent_id) if isinstance(parent_id, int) else parent_id
        if nsfw is not None:
            data["nsfw"] = nsfw
        return await self.request("POST", f"/guilds/{guild_id}/channels", json=data)
    
    async def modify_channel(self, channel_id: int, **kwargs) -> Dict:
        """Изменить канал"""
        return await self.request("PATCH", f"/channels/{channel_id}", json=kwargs)
    
    async def delete_channel(self, channel_id: int) -> Dict:
        """Удалить канал"""
        return await self.request("DELETE", f"/channels/{channel_id}")
    
    async def get_channel_invites(self, channel_id: int) -> list:
        """Получить приглашения канала"""
        return await self.request("GET", f"/channels/{channel_id}/invites")
    
    async def create_channel_invite(
        self,
        channel_id: int,
        max_age: int = 86400,
        max_uses: int = 0,
        temporary: bool = False,
        unique: bool = True,
        target_type: Optional[int] = None,
        target_user_id: Optional[int] = None,
        target_application_id: Optional[int] = None
    ) -> Dict:
        """Создать приглашение в канал"""
        data = {
            "max_age": max_age,
            "max_uses": max_uses,
            "temporary": temporary,
            "unique": unique
        }
        if target_type:
            data["target_type"] = target_type
        if target_user_id:
            data["target_user_id"] = target_user_id
        if target_application_id:
            data["target_application_id"] = target_application_id
        return await self.request("POST", f"/channels/{channel_id}/invites", json=data)
    
    # ========== Методы для работы с участниками ==========
    
    async def remove_guild_member(self, guild_id: int, user_id: int, reason: Optional[str] = None):
        """Удалить участника из гильдии"""
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        return await self.request("DELETE", f"/guilds/{guild_id}/members/{user_id}", headers=headers)
    
    async def get_guild_bans(self, guild_id: int, limit: int = 1000, before: Optional[int] = None, after: Optional[int] = None) -> list:
        """Получить список банов гильдии"""
        params = {"limit": limit}
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return await self.request("GET", f"/guilds/{guild_id}/bans", params=params)
    
    async def get_guild_ban(self, guild_id: int, user_id: int) -> Dict:
        """Получить бан пользователя"""
        return await self.request("GET", f"/guilds/{guild_id}/bans/{user_id}")
    
    async def create_guild_ban(
        self,
        guild_id: int,
        user_id: int,
        delete_message_days: int = 0,
        reason: Optional[str] = None
    ):
        """Забанить пользователя"""
        data = {"delete_message_days": delete_message_days}
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        return await self.request("PUT", f"/guilds/{guild_id}/bans/{user_id}", json=data, headers=headers)
    
    async def remove_guild_ban(self, guild_id: int, user_id: int, reason: Optional[str] = None):
        """Разбанить пользователя"""
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        return await self.request("DELETE", f"/guilds/{guild_id}/bans/{user_id}", headers=headers)
    
    async def modify_guild_member_nick(self, guild_id: int, user_id: int, nick: Optional[str] = None):
        """Изменить никнейм участника"""
        return await self.modify_guild_member(guild_id, user_id, nick=nick)
    
    # ========== Методы для работы с эмодзи ==========
    
    async def list_guild_emojis(self, guild_id: int) -> list:
        """Получить список эмодзи гильдии"""
        return await self.request("GET", f"/guilds/{guild_id}/emojis")
    
    async def get_guild_emoji(self, guild_id: int, emoji_id: int) -> Dict:
        """Получить эмодзи гильдии"""
        return await self.request("GET", f"/guilds/{guild_id}/emojis/{emoji_id}")
    
    async def create_guild_emoji(
        self,
        guild_id: int,
        name: str,
        image: str,
        roles: Optional[list] = None,
        reason: Optional[str] = None
    ) -> Dict:
        """Создать эмодзи в гильдии"""
        data = {"name": name, "image": image}
        if roles:
            data["roles"] = roles
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        return await self.request("POST", f"/guilds/{guild_id}/emojis", json=data, headers=headers)
    
    async def modify_guild_emoji(
        self,
        guild_id: int,
        emoji_id: int,
        name: Optional[str] = None,
        roles: Optional[list] = None,
        reason: Optional[str] = None
    ) -> Dict:
        """Изменить эмодзи гильдии"""
        data = {}
        if name:
            data["name"] = name
        if roles:
            data["roles"] = roles
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        return await self.request("PATCH", f"/guilds/{guild_id}/emojis/{emoji_id}", json=data, headers=headers)
    
    async def delete_guild_emoji(self, guild_id: int, emoji_id: int, reason: Optional[str] = None):
        """Удалить эмодзи гильдии"""
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        return await self.request("DELETE", f"/guilds/{guild_id}/emojis/{emoji_id}", headers=headers)
    
    # ========== Методы для работы с гильдиями ==========
    
    async def modify_guild(
        self,
        guild_id: int,
        name: Optional[str] = None,
        verification_level: Optional[int] = None,
        default_message_notifications: Optional[int] = None,
        explicit_content_filter: Optional[int] = None,
        afk_channel_id: Optional[int] = None,
        afk_timeout: Optional[int] = None,
        icon: Optional[str] = None,
        owner_id: Optional[int] = None,
        splash: Optional[str] = None,
        banner: Optional[str] = None,
        system_channel_id: Optional[int] = None,
        rules_channel_id: Optional[int] = None,
        public_updates_channel_id: Optional[int] = None,
        preferred_locale: Optional[str] = None,
        reason: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """Изменить гильдию"""
        data = {}
        for key, value in locals().items():
            if key not in ["self", "guild_id", "reason", "kwargs", "data"] and value is not None:
                data[key] = value
        data.update(kwargs)
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        return await self.request("PATCH", f"/guilds/{guild_id}", json=data, headers=headers)
    
    async def delete_guild(self, guild_id: int):
        """Удалить гильдию"""
        return await self.request("DELETE", f"/guilds/{guild_id}")
    
    async def get_guild_invites(self, guild_id: int) -> list:
        """Получить приглашения гильдии"""
        return await self.request("GET", f"/guilds/{guild_id}/invites")
    
    async def get_guild_voice_regions(self, guild_id: int) -> list:
        """Получить голосовые регионы гильдии"""
        return await self.request("GET", f"/guilds/{guild_id}/regions")
    
    async def get_guild_audit_logs(
        self,
        guild_id: int,
        user_id: Optional[int] = None,
        action_type: Optional[int] = None,
        before: Optional[int] = None,
        limit: int = 50
    ) -> Dict:
        """Получить логи аудита гильдии"""
        params = {"limit": min(limit, 100)}
        if user_id:
            params["user_id"] = user_id
        if action_type:
            params["action_type"] = action_type
        if before:
            params["before"] = before
        return await self.request("GET", f"/guilds/{guild_id}/audit-logs", params=params)
    
    # ========== Методы для работы с webhooks ==========
    
    async def create_webhook(
        self,
        channel_id: int,
        name: str,
        avatar: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict:
        """Создать webhook"""
        data = {"name": name}
        if avatar:
            data["avatar"] = avatar
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        return await self.request("POST", f"/channels/{channel_id}/webhooks", json=data, headers=headers)
    
    async def get_channel_webhooks(self, channel_id: int) -> list:
        """Получить webhooks канала"""
        return await self.request("GET", f"/channels/{channel_id}/webhooks")
    
    async def get_guild_webhooks(self, guild_id: int) -> list:
        """Получить webhooks гильдии"""
        return await self.request("GET", f"/guilds/{guild_id}/webhooks")
    
    async def get_webhook(self, webhook_id: int) -> Dict:
        """Получить webhook"""
        return await self.request("GET", f"/webhooks/{webhook_id}")
    
    async def get_webhook_with_token(self, webhook_id: int, webhook_token: str) -> Dict:
        """Получить webhook с токеном"""
        return await self.request("GET", f"/webhooks/{webhook_id}/{webhook_token}")
    
    async def modify_webhook(
        self,
        webhook_id: int,
        name: Optional[str] = None,
        avatar: Optional[str] = None,
        channel_id: Optional[int] = None,
        reason: Optional[str] = None
    ) -> Dict:
        """Изменить webhook"""
        data = {}
        if name:
            data["name"] = name
        if avatar:
            data["avatar"] = avatar
        if channel_id:
            data["channel_id"] = channel_id
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        return await self.request("PATCH", f"/webhooks/{webhook_id}", json=data, headers=headers)
    
    async def modify_webhook_with_token(
        self,
        webhook_id: int,
        webhook_token: str,
        name: Optional[str] = None,
        avatar: Optional[str] = None
    ) -> Dict:
        """Изменить webhook с токеном"""
        data = {}
        if name:
            data["name"] = name
        if avatar:
            data["avatar"] = avatar
        return await self.request("PATCH", f"/webhooks/{webhook_id}/{webhook_token}", json=data)
    
    async def delete_webhook(self, webhook_id: int, reason: Optional[str] = None):
        """Удалить webhook"""
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason
        return await self.request("DELETE", f"/webhooks/{webhook_id}", headers=headers)
    
    async def delete_webhook_with_token(self, webhook_id: int, webhook_token: str):
        """Удалить webhook с токеном"""
        return await self.request("DELETE", f"/webhooks/{webhook_id}/{webhook_token}")
    
    async def execute_webhook(
        self,
        webhook_id: int,
        webhook_token: str,
        content: Optional[str] = None,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
        tts: bool = False,
        embeds: Optional[list] = None,
        components: Optional[list] = None,
        files: Optional[list] = None,
        allowed_mentions: Optional[Dict] = None,
        flags: Optional[int] = None,
        thread_id: Optional[int] = None,
        wait: bool = False
    ) -> Optional[Dict]:
        """Выполнить webhook (отправить сообщение через webhook)"""
        url = f"/webhooks/{webhook_id}/{webhook_token}"
        if wait:
            url += "?wait=true"
        
        # Если есть файлы, используем multipart
        if files:
            return await self._execute_webhook_with_files(
                webhook_id, webhook_token, content, username, avatar_url,
                tts, embeds, components, files, allowed_mentions, flags, thread_id, wait
            )
        
        data = {}
        if content:
            data["content"] = content
        if username:
            data["username"] = username
        if avatar_url:
            data["avatar_url"] = avatar_url
        if tts:
            data["tts"] = tts
        if embeds:
            data["embeds"] = embeds
        if components:
            data["components"] = components
        if allowed_mentions:
            data["allowed_mentions"] = allowed_mentions
        if flags is not None:
            data["flags"] = flags
        if thread_id:
            data["thread_id"] = thread_id
        
        return await self.request("POST", url, json=data)
    
    async def _execute_webhook_with_files(
        self,
        webhook_id: int,
        webhook_token: str,
        content: Optional[str] = None,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
        tts: bool = False,
        embeds: Optional[list] = None,
        components: Optional[list] = None,
        files: Optional[list] = None,
        allowed_mentions: Optional[Dict] = None,
        flags: Optional[int] = None,
        thread_id: Optional[int] = None,
        wait: bool = False
    ) -> Optional[Dict]:
        """Выполнить webhook с файлами"""
        if not self.session:
            await self.start()
        
        url = f"{self.BASE_URL}/webhooks/{webhook_id}/{webhook_token}"
        if wait:
            url += "?wait=true"
        
        headers = {"User-Agent": self.user_agent}
        
        form_data = aiohttp.FormData()
        
        payload = {}
        if content:
            payload["content"] = content
        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url
        if tts:
            payload["tts"] = tts
        if embeds:
            payload["embeds"] = embeds
        if components:
            payload["components"] = components
        if allowed_mentions:
            payload["allowed_mentions"] = allowed_mentions
        if flags is not None:
            payload["flags"] = flags
        if thread_id:
            payload["thread_id"] = thread_id
        
        form_data.add_field("payload_json", json.dumps(payload), content_type="application/json")
        
        for i, file_data in enumerate(files):
            if isinstance(file_data, dict):
                filename = file_data.get("filename", f"file{i}.png")
                file_obj = file_data.get("file")
                content_type = file_data.get("content_type", "application/octet-stream")
                form_data.add_field(f"files[{i}]", file_obj, filename=filename, content_type=content_type)
            else:
                form_data.add_field(f"files[{i}]", file_data, filename=f"file{i}.png")
        
        try:
            async with self.session.post(url, headers=headers, data=form_data) as response:
                if response.status == 204:
                    return None
                
                try:
                    data = await response.json()
                except:
                    data = await response.text()
                
                if response.status >= 400:
                    raise HTTPException(response, data)
                
                return data
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise HTTPException(None, str(e))
    
    async def edit_webhook_message(
        self,
        webhook_id: int,
        webhook_token: str,
        message_id: int,
        content: Optional[str] = None,
        embeds: Optional[list] = None,
        components: Optional[list] = None,
        files: Optional[list] = None,
        allowed_mentions: Optional[Dict] = None
    ) -> Dict:
        """Редактировать сообщение webhook"""
        url = f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}"
        
        if files:
            return await self._edit_webhook_message_with_files(
                webhook_id, webhook_token, message_id, content,
                embeds, components, files, allowed_mentions
            )
        
        data = {}
        if content:
            data["content"] = content
        if embeds:
            data["embeds"] = embeds
        if components:
            data["components"] = components
        if allowed_mentions:
            data["allowed_mentions"] = allowed_mentions
        
        return await self.request("PATCH", url, json=data)
    
    async def _edit_webhook_message_with_files(
        self,
        webhook_id: int,
        webhook_token: str,
        message_id: int,
        content: Optional[str] = None,
        embeds: Optional[list] = None,
        components: Optional[list] = None,
        files: Optional[list] = None,
        allowed_mentions: Optional[Dict] = None
    ) -> Dict:
        """Редактировать сообщение webhook с файлами"""
        if not self.session:
            await self.start()
        
        url = f"{self.BASE_URL}/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}"
        headers = {"User-Agent": self.user_agent}
        
        form_data = aiohttp.FormData()
        
        payload = {}
        if content:
            payload["content"] = content
        if embeds:
            payload["embeds"] = embeds
        if components:
            payload["components"] = components
        if allowed_mentions:
            payload["allowed_mentions"] = allowed_mentions
        
        form_data.add_field("payload_json", json.dumps(payload), content_type="application/json")
        
        for i, file_data in enumerate(files):
            if isinstance(file_data, dict):
                filename = file_data.get("filename", f"file{i}.png")
                file_obj = file_data.get("file")
                content_type = file_data.get("content_type", "application/octet-stream")
                form_data.add_field(f"files[{i}]", file_obj, filename=filename, content_type=content_type)
            else:
                form_data.add_field(f"files[{i}]", file_data, filename=f"file{i}.png")
        
        try:
            async with self.session.patch(url, headers=headers, data=form_data) as response:
                try:
                    data = await response.json()
                except:
                    data = await response.text()
                
                if response.status >= 400:
                    raise HTTPException(response, data)
                
                return data
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise HTTPException(None, str(e))
    
    async def delete_webhook_message(
        self,
        webhook_id: int,
        webhook_token: str,
        message_id: int
    ):
        """Удалить сообщение webhook"""
        return await self.request("DELETE", f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}")
    
    # ========== Методы для работы с нитями (threads) ==========
    
    async def start_thread_with_message(
        self,
        channel_id: int,
        message_id: int,
        name: str,
        auto_archive_duration: Optional[int] = None
    ) -> Dict:
        """Создать нить из сообщения"""
        data = {"name": name}
        if auto_archive_duration:
            data["auto_archive_duration"] = auto_archive_duration
        return await self.request("POST", f"/channels/{channel_id}/messages/{message_id}/threads", json=data)
    
    async def start_thread_without_message(
        self,
        channel_id: int,
        name: str,
        auto_archive_duration: Optional[int] = None,
        type: Optional[int] = None,
        invitable: Optional[bool] = None
    ) -> Dict:
        """Создать нить без сообщения"""
        data = {"name": name}
        if auto_archive_duration:
            data["auto_archive_duration"] = auto_archive_duration
        if type:
            data["type"] = type
        if invitable is not None:
            data["invitable"] = invitable
        return await self.request("POST", f"/channels/{channel_id}/threads", json=data)
    
    async def join_thread(self, channel_id: int):
        """Присоединиться к нити"""
        return await self.request("PUT", f"/channels/{channel_id}/thread-members/@me")
    
    async def leave_thread(self, channel_id: int):
        """Покинуть нить"""
        return await self.request("DELETE", f"/channels/{channel_id}/thread-members/@me")
    
    async def add_thread_member(self, channel_id: int, user_id: int):
        """Добавить участника в нить"""
        return await self.request("PUT", f"/channels/{channel_id}/thread-members/{user_id}")
    
    async def remove_thread_member(self, channel_id: int, user_id: int):
        """Удалить участника из нити"""
        return await self.request("DELETE", f"/channels/{channel_id}/thread-members/{user_id}")
    
    async def get_thread_member(self, channel_id: int, user_id: int) -> Dict:
        """Получить участника нити"""
        return await self.request("GET", f"/channels/{channel_id}/thread-members/{user_id}")
    
    async def list_thread_members(self, channel_id: int) -> list:
        """Получить список участников нити"""
        return await self.request("GET", f"/channels/{channel_id}/thread-members")
    
    async def list_active_threads(self, guild_id: int) -> Dict:
        """Получить активные нити гильдии"""
        return await self.request("GET", f"/guilds/{guild_id}/threads/active")
    
    async def list_public_archived_threads(
        self,
        channel_id: int,
        before: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict:
        """Получить публичные архивированные нити"""
        params = {}
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        return await self.request("GET", f"/channels/{channel_id}/threads/archived/public", params=params)
    
    async def list_private_archived_threads(
        self,
        channel_id: int,
        before: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict:
        """Получить приватные архивированные нити"""
        params = {}
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        return await self.request("GET", f"/channels/{channel_id}/threads/archived/private", params=params)
    
    async def list_joined_private_archived_threads(
        self,
        channel_id: int,
        before: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict:
        """Получить присоединенные приватные архивированные нити"""
        params = {}
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit
        return await self.request("GET", f"/channels/{channel_id}/users/@me/threads/archived/private", params=params)

