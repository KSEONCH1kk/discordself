"""Класс для работы с Webhooks"""

from typing import Optional, Dict, List
from .http import HTTPClient
from .models import Message
from .embeds import Embed, ActionRow


class Webhook:
    """Класс для работы с Discord Webhook"""
    
    def __init__(self, webhook_id: int, webhook_token: str, http_client: Optional[HTTPClient] = None):
        self.id = webhook_id
        self.token = webhook_token
        self._http = http_client
    
    async def send(
        self,
        content: Optional[str] = None,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
        tts: bool = False,
        embeds: Optional[List] = None,
        components: Optional[List] = None,
        files: Optional[List] = None,
        allowed_mentions: Optional[Dict] = None,
        flags: Optional[int] = None,
        thread_id: Optional[int] = None,
        wait: bool = False
    ) -> Optional[Message]:
        """Отправить сообщение через webhook"""
        if not self._http:
            raise RuntimeError("HTTP client not initialized")
        
        # Преобразовать embeds если это объекты Embed
        if embeds:
            embeds = [e.to_dict() if hasattr(e, 'to_dict') else e for e in embeds]
        
        # Преобразовать components если это объекты ActionRow
        if components:
            components = [c.to_dict() if hasattr(c, 'to_dict') else c for c in components]
        
        data = await self._http.execute_webhook(
            self.id, self.token, content, username, avatar_url,
            tts, embeds, components, files, allowed_mentions,
            flags, thread_id, wait
        )
        
        if data and wait:
            return Message(data, None)  # Webhook сообщения не имеют клиента
        return None
    
    async def edit_message(
        self,
        message_id: int,
        content: Optional[str] = None,
        embeds: Optional[List] = None,
        components: Optional[List] = None,
        files: Optional[List] = None,
        allowed_mentions: Optional[Dict] = None
    ) -> Message:
        """Редактировать сообщение webhook"""
        if not self._http:
            raise RuntimeError("HTTP client not initialized")
        
        # Преобразовать embeds если это объекты Embed
        if embeds:
            embeds = [e.to_dict() if hasattr(e, 'to_dict') else e for e in embeds]
        
        # Преобразовать components если это объекты ActionRow
        if components:
            components = [c.to_dict() if hasattr(c, 'to_dict') else c for c in components]
        
        data = await self._http.edit_webhook_message(
            self.id, self.token, message_id, content,
            embeds, components, files, allowed_mentions
        )
        return Message(data, None)
    
    async def delete_message(self, message_id: int):
        """Удалить сообщение webhook"""
        if not self._http:
            raise RuntimeError("HTTP client not initialized")
        return await self._http.delete_webhook_message(self.id, self.token, message_id)
    
    async def get_info(self) -> Dict:
        """Получить информацию о webhook"""
        if not self._http:
            raise RuntimeError("HTTP client not initialized")
        return await self._http.get_webhook_with_token(self.id, self.token)
    
    async def modify(
        self,
        name: Optional[str] = None,
        avatar: Optional[str] = None
    ) -> Dict:
        """Изменить webhook"""
        if not self._http:
            raise RuntimeError("HTTP client not initialized")
        return await self._http.modify_webhook_with_token(self.id, self.token, name, avatar)
    
    async def delete(self):
        """Удалить webhook"""
        if not self._http:
            raise RuntimeError("HTTP client not initialized")
        return await self._http.delete_webhook_with_token(self.id, self.token)

