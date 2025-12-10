"""Скрипт для копирования Discord сервера"""

import asyncio
import os
import base64
from discordself import Client
from typing import Dict, List, Optional

TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_TOKEN_HERE")


class ServerCopier:
    """Класс для копирования Discord сервера"""
    
    def __init__(self, client: Client):
        self.client = client
        self.http = client.http
    
    async def download_image(self, url: str) -> Optional[str]:
        """Скачать изображение и преобразовать в base64"""
        if not url:
            return None
        
        try:
            # Использовать сессию из HTTP клиента
            if not self.http.session:
                await self.http.start()
            
            async with self.http.session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    # Определить формат
                    if url.endswith('.png'):
                        return f"data:image/png;base64,{base64_data}"
                    elif url.endswith('.jpg') or url.endswith('.jpeg'):
                        return f"data:image/jpeg;base64,{base64_data}"
                    elif url.endswith('.gif'):
                        return f"data:image/gif;base64,{base64_data}"
                    else:
                        return f"data:image/png;base64,{base64_data}"
        except Exception as e:
            print(f"Ошибка при загрузке изображения {url}: {e}")
            return None
    
    async def get_guild_data(self, guild_id: int) -> Dict:
        """Получить все данные о гильдии"""
        print(f"📥 Получение данных о сервере {guild_id}...")
        
        # Получить основную информацию о гильдии
        guild = await self.client.fetch_guild(guild_id)
        guild_data = {
            "id": guild.id,
            "name": guild.name,
            "description": guild.description,
            "icon": guild.icon,
            "banner": guild.banner,
            "splash": guild.splash,
            "verification_level": guild.verification_level,
            "default_message_notifications": guild.default_message_notifications,
            "explicit_content_filter": guild.explicit_content_filter,
            "afk_channel_id": guild.afk_channel_id,
            "afk_timeout": guild.afk_timeout,
            "system_channel_id": guild.system_channel_id,
            "system_channel_flags": guild.system_channel_flags,
            "rules_channel_id": guild.rules_channel_id,
            "public_updates_channel_id": guild.public_updates_channel_id,
            "preferred_locale": guild.preferred_locale,
            "premium_tier": guild.premium_tier,
            "nsfw_level": guild.nsfw_level,
        }
        
        # Получить каналы
        print("📁 Получение каналов...")
        channels_data = await self.http.get_guild_channels(guild_id)
        guild_data["channels"] = channels_data
        
        # Получить роли
        print("👥 Получение ролей...")
        roles_data = await self.http.get_guild_roles(guild_id)
        guild_data["roles"] = roles_data
        
        # Получить эмодзи
        print("😀 Получение эмодзи...")
        emojis_data = await self.http.list_guild_emojis(guild_id)
        guild_data["emojis"] = emojis_data
        
        # Получить приглашения
        print("🔗 Получение приглашений...")
        try:
            invites_data = await self.http.get_guild_invites(guild_id)
            guild_data["invites"] = invites_data
        except:
            guild_data["invites"] = []
        
        print(f"✅ Данные о сервере получены!")
        return guild_data
    
    async def create_guild_from_data(self, source_data: Dict, new_name: Optional[str] = None) -> int:
        """Создать новую гильдию на основе данных"""
        print(f"🏗️  Создание нового сервера...")
        
        # Подготовить данные для создания
        name = new_name or f"{source_data['name']} (Copy)"
        
        # Скачать иконку
        icon_data = None
        if source_data.get("icon"):
            icon_url = f"https://cdn.discordapp.com/icons/{source_data['id']}/{source_data['icon']}.png"
            icon_data = await self.download_image(icon_url)
        
        # Роли будут созданы отдельно после создания гильдии
        roles = []
        
        # Создать гильдию
        guild_data = await self.http.create_guild(
            name=name,
            icon=icon_data,
            verification_level=source_data.get("verification_level"),
            default_message_notifications=source_data.get("default_message_notifications"),
            explicit_content_filter=source_data.get("explicit_content_filter"),
            roles=roles
        )
        
        new_guild_id = int(guild_data["id"])
        print(f"✅ Сервер создан! ID: {new_guild_id}")
        
        return new_guild_id
    
    def update_permission_overwrites(self, overwrites: List[Dict], role_mapping: Dict) -> List[Dict]:
        """Обновить permission_overwrites с учетом маппинга ролей"""
        updated = []
        for overwrite in overwrites:
            overwrite_id = int(overwrite.get("id", 0))
            overwrite_type = overwrite.get("type", 0)
            
            # Если это роль и есть маппинг
            if overwrite_type == 0 and overwrite_id in role_mapping:
                new_overwrite = overwrite.copy()
                new_overwrite["id"] = str(role_mapping[overwrite_id])
                updated.append(new_overwrite)
            # Если это пользователь, пропускаем (пользователи не копируются)
            elif overwrite_type == 1:
                pass
            else:
                updated.append(overwrite)
        return updated
    
    async def copy_channels(self, source_guild_id: int, target_guild_id: int, channels_data: List[Dict], role_mapping: Dict = None):
        """Скопировать каналы"""
        print(f"📁 Копирование каналов...")
        
        if role_mapping is None:
            role_mapping = {}
        
        # Создать маппинг старых ID на новые
        channel_mapping = {}
        
        # Сначала создать категории
        categories = [ch for ch in channels_data if ch.get("type") == 4]
        # Сортировать по position
        categories.sort(key=lambda x: x.get("position", 0))
        
        for category in categories:
            try:
                # Обновить permission_overwrites с маппингом ролей
                permission_overwrites = self.update_permission_overwrites(
                    category.get("permission_overwrites", []),
                    role_mapping
                )
                
                new_channel = await self.http.create_channel(
                    guild_id=target_guild_id,
                    name=category.get("name", "Category"),
                    type=4,  # Category
                    position=category.get("position", 0),
                    permission_overwrites=permission_overwrites
                )
                channel_mapping[int(category["id"])] = int(new_channel["id"])
                print(f"  ✅ Категория: {category.get('name')}")
                await asyncio.sleep(0.5)  # Задержка для rate limit
            except Exception as e:
                print(f"  ❌ Ошибка при создании категории {category.get('name')}: {e}")
        
        # Затем создать остальные каналы
        other_channels = [ch for ch in channels_data if ch.get("type") != 4]
        # Сортировать по position
        other_channels.sort(key=lambda x: x.get("position", 0))
        
        for channel in other_channels:
            try:
                # Обновить parent_id если есть
                parent_id = channel.get("parent_id")
                if parent_id:
                    parent_id = int(parent_id)
                    if parent_id in channel_mapping:
                        parent_id = channel_mapping[parent_id]
                    else:
                        parent_id = None
                else:
                    parent_id = None
                
                channel_type = channel.get("type", 0)
                
                # Обновить permission_overwrites
                permission_overwrites = self.update_permission_overwrites(
                    channel.get("permission_overwrites", []),
                    role_mapping
                )
                
                new_channel = await self.http.create_channel(
                    guild_id=target_guild_id,
                    name=channel.get("name", "channel"),
                    type=channel_type,
                    topic=channel.get("topic"),
                    bitrate=channel.get("bitrate"),
                    user_limit=channel.get("user_limit"),
                    rate_limit_per_user=channel.get("rate_limit_per_user"),
                    position=channel.get("position", 0),
                    permission_overwrites=permission_overwrites,
                    parent_id=parent_id,
                    nsfw=channel.get("nsfw", False)
                )
                channel_mapping[int(channel["id"])] = int(new_channel["id"])
                print(f"  ✅ Канал: {channel.get('name')} (тип: {channel_type})")
                await asyncio.sleep(0.5)  # Задержка для rate limit
            except Exception as e:
                print(f"  ❌ Ошибка при создании канала {channel.get('name')}: {e}")
        
        return channel_mapping
    
    async def copy_roles(self, source_guild_id: int, target_guild_id: int, roles_data: List[Dict]):
        """Скопировать роли"""
        print(f"👥 Копирование ролей...")
        
        role_mapping = {}
        
        # Пропустить @everyone роль
        roles_to_copy = [r for r in roles_data if r.get("name") != "@everyone"]
        
        # Сортировать по position (от большего к меньшему)
        roles_to_copy.sort(key=lambda x: x.get("position", 0), reverse=True)
        
        for role in roles_to_copy:
            try:
                new_role = await self.http.create_guild_role(
                    guild_id=target_guild_id,
                    name=role.get("name", "New Role"),
                    permissions=str(role.get("permissions", "0")),
                    color=role.get("color", 0),
                    hoist=role.get("hoist", False),
                    mentionable=role.get("mentionable", False)
                )
                role_mapping[int(role["id"])] = int(new_role["id"])
                print(f"  ✅ Роль: {role.get('name')}")
                await asyncio.sleep(0.5)  # Задержка для rate limit
            except Exception as e:
                print(f"  ❌ Ошибка при создании роли {role.get('name')}: {e}")
        
        return role_mapping
    
    async def copy_emojis(self, source_guild_id: int, target_guild_id: int, emojis_data: List[Dict]):
        """Скопировать эмодзи"""
        print(f"😀 Копирование эмодзи...")
        
        for emoji in emojis_data:
            try:
                # Скачать эмодзи
                emoji_id = emoji.get("id")
                emoji_name = emoji.get("name")
                animated = emoji.get("animated", False)
                
                extension = "gif" if animated else "png"
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{extension}"
                
                emoji_data = await self.download_image(emoji_url)
                
                if emoji_data:
                    # Создать эмодзи
                    await self.http.create_guild_emoji(
                        guild_id=target_guild_id,
                        name=emoji_name,
                        image=emoji_data,
                        roles=emoji.get("roles", [])
                    )
                    print(f"  ✅ Эмодзи: {emoji_name}")
                    await asyncio.sleep(1)  # Задержка для rate limit
            except Exception as e:
                print(f"  ❌ Ошибка при создании эмодзи {emoji.get('name')}: {e}")
    
    async def update_guild_settings(self, target_guild_id: int, source_data: Dict, channel_mapping: Dict):
        """Обновить настройки гильдии"""
        print(f"⚙️  Обновление настроек сервера...")
        
        try:
            # Обновить afk_channel_id если есть
            afk_channel_id = source_data.get("afk_channel_id")
            if afk_channel_id:
                afk_channel_id = int(afk_channel_id)
                if afk_channel_id in channel_mapping:
                    afk_channel_id = channel_mapping[afk_channel_id]
                else:
                    afk_channel_id = None
            
            # Обновить system_channel_id если есть
            system_channel_id = source_data.get("system_channel_id")
            if system_channel_id:
                system_channel_id = int(system_channel_id)
                if system_channel_id in channel_mapping:
                    system_channel_id = channel_mapping[system_channel_id]
                else:
                    system_channel_id = None
            
            # Обновить rules_channel_id если есть
            rules_channel_id = source_data.get("rules_channel_id")
            if rules_channel_id:
                rules_channel_id = int(rules_channel_id)
                if rules_channel_id in channel_mapping:
                    rules_channel_id = channel_mapping[rules_channel_id]
                else:
                    rules_channel_id = None
            
            # Обновить public_updates_channel_id если есть
            public_updates_channel_id = source_data.get("public_updates_channel_id")
            if public_updates_channel_id:
                public_updates_channel_id = int(public_updates_channel_id)
                if public_updates_channel_id in channel_mapping:
                    public_updates_channel_id = channel_mapping[public_updates_channel_id]
                else:
                    public_updates_channel_id = None
            
            # Скачать баннер если есть
            banner_data = None
            if source_data.get("banner"):
                banner_url = f"https://cdn.discordapp.com/banners/{source_data['id']}/{source_data['banner']}.png"
                banner_data = await self.download_image(banner_url)
            
            # Скачать splash если есть
            splash_data = None
            if source_data.get("splash"):
                splash_url = f"https://cdn.discordapp.com/splashes/{source_data['id']}/{source_data['splash']}.png"
                splash_data = await self.download_image(splash_url)
            
            # Обновить гильдию
            await self.http.modify_guild(
                guild_id=target_guild_id,
                name=source_data.get("name"),
                description=source_data.get("description"),
                verification_level=source_data.get("verification_level"),
                default_message_notifications=source_data.get("default_message_notifications"),
                explicit_content_filter=source_data.get("explicit_content_filter"),
                afk_channel_id=afk_channel_id,
                afk_timeout=source_data.get("afk_timeout"),
                system_channel_id=system_channel_id,
                system_channel_flags=source_data.get("system_channel_flags"),
                rules_channel_id=rules_channel_id,
                public_updates_channel_id=public_updates_channel_id,
                preferred_locale=source_data.get("preferred_locale"),
                banner=banner_data,
                splash=splash_data
            )
            
            print(f"✅ Настройки сервера обновлены!")
        except Exception as e:
            print(f"❌ Ошибка при обновлении настроек: {e}")
    
    async def copy_server(self, from_guild_id: int, to_guild_id: Optional[int] = None, new_name: Optional[str] = None):
        """Скопировать сервер"""
        print(f"🚀 Начало копирования сервера {from_guild_id}...")
        
        # Получить данные исходного сервера
        source_data = await self.get_guild_data(from_guild_id)
        
        # Создать новый сервер или использовать существующий
        if to_guild_id:
            target_guild_id = to_guild_id
            print(f"📌 Использование существующего сервера {target_guild_id}")
        else:
            target_guild_id = await self.create_guild_from_data(source_data, new_name)
        
        # Копировать роли (получить маппинг)
        role_mapping = await self.copy_roles(
            from_guild_id,
            target_guild_id,
            source_data.get("roles", [])
        )
        
        # Копировать каналы (с учетом маппинга ролей)
        channel_mapping = await self.copy_channels(
            from_guild_id,
            target_guild_id,
            source_data.get("channels", []),
            role_mapping
        )
        
        # Копировать эмодзи
        await self.copy_emojis(
            from_guild_id,
            target_guild_id,
            source_data.get("emojis", [])
        )
        
        # Обновить настройки гильдии
        await self.update_guild_settings(target_guild_id, source_data, channel_mapping)
        
        print(f"✅ Копирование завершено! Новый сервер: {target_guild_id}")
        return target_guild_id


async def main():
    """Главная функция"""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python copy_server.py <from_guild_id> [to_guild_id] [new_name]")
        print("Пример: python copy_server.py 123456789")
        print("Пример: python copy_server.py 123456789 987654321")
        print("Пример: python copy_server.py 123456789 None 'Новое имя'")
        sys.exit(1)
    
    from_guild_id = int(sys.argv[1])
    to_guild_id = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] != "None" else None
    new_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    client = Client(token=TOKEN)
    
    try:
        await client.login()
        print(f"✅ Вход выполнен как {client.user}")
        
        copier = ServerCopier(client)
        await copier.copy_server(from_guild_id, to_guild_id, new_name)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
