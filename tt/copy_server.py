"""Скрипт для копирования Discord сервера"""

import asyncio
import os
import base64
from discordself import Client, Intents
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
    
    def update_permission_overwrites(self, overwrites: List[Dict], role_mapping: Dict, source_guild_id: int, target_guild_id: int) -> List[Dict]:
        """Обновить permission_overwrites с учетом маппинга ролей"""
        updated = []
        if not overwrites:
            return updated
        
        for overwrite in overwrites:
            # Получить ID (может быть строкой или числом)
            overwrite_id_raw = overwrite.get("id")
            if overwrite_id_raw is None:
                continue
            
            overwrite_id = int(overwrite_id_raw) if isinstance(overwrite_id_raw, (str, int)) else 0
            overwrite_type = int(overwrite.get("type", 0))
            
            # Получить allow и deny (могут быть строками или числами)
            allow = overwrite.get("allow", "0")
            deny = overwrite.get("deny", "0")
            
            # Преобразовать в строки если нужно
            if isinstance(allow, (int, float)):
                allow = str(int(allow))
            else:
                allow = str(allow) if allow else "0"
            
            if isinstance(deny, (int, float)):
                deny = str(int(deny))
            else:
                deny = str(deny) if deny else "0"
            
            # Если это роль (type 0)
            if overwrite_type == 0:
                # Если это @everyone роль (ID совпадает с ID исходной гильдии)
                if overwrite_id == source_guild_id:
                    new_overwrite = {
                        "id": str(target_guild_id),  # @everyone роль в целевой гильдии
                        "type": 0,
                        "allow": allow,
                        "deny": deny
                    }
                    updated.append(new_overwrite)
                # Если есть маппинг для этой роли
                elif overwrite_id in role_mapping:
                    new_overwrite = {
                        "id": str(role_mapping[overwrite_id]),
                        "type": 0,
                        "allow": allow,
                        "deny": deny
                    }
                    updated.append(new_overwrite)
                # Если роли нет в маппинге, пропускаем (роль не была скопирована)
                else:
                    pass
            # Если это пользователь (type 1), пропускаем (пользователи не копируются)
            elif overwrite_type == 1:
                pass
            else:
                # Для других типов оставляем как есть
                new_overwrite = {
                    "id": str(overwrite_id),
                    "type": overwrite_type,
                    "allow": allow,
                    "deny": deny
                }
                updated.append(new_overwrite)
        
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
                original_overwrites = category.get("permission_overwrites", [])
                permission_overwrites = self.update_permission_overwrites(
                    original_overwrites,
                    role_mapping,
                    source_guild_id,
                    target_guild_id
                )
                
                # Отладочная информация
                if original_overwrites and not permission_overwrites:
                    print(f"    ⚠️ Внимание: у категории {category.get('name')} были permissions, но они не были применены (возможно, роли не найдены)")
                
                # Подготовить параметры для создания канала
                channel_params = {
                    "guild_id": target_guild_id,
                    "name": category.get("name", "Category"),
                    "type": 4,  # Category
                    "position": category.get("position", 0)
                }
                
                # Добавить permission_overwrites только если они есть
                if permission_overwrites:
                    channel_params["permission_overwrites"] = permission_overwrites
                
                new_channel = await self.http.create_channel(**channel_params)
                channel_id = int(new_channel["id"])
                channel_mapping[int(category["id"])] = channel_id
                
                # Если есть permissions, обновить их после создания (на случай если не применились)
                if permission_overwrites:
                    try:
                        await asyncio.sleep(0.2)  # Небольшая задержка перед обновлением
                        await self.http.modify_channel(
                            channel_id,
                            permission_overwrites=permission_overwrites
                        )
                        print(f"  ✅ Категория: {category.get('name')} (permissions: {len(permission_overwrites)})")
                    except Exception as perm_error:
                        print(f"  ⚠️ Категория: {category.get('name')} создана, но permissions не обновлены: {perm_error}")
                else:
                    print(f"  ✅ Категория: {category.get('name')}")
                
                await asyncio.sleep(0.5)  # Задержка для rate limit
            except Exception as e:
                print(f"  ❌ Ошибка при создании категории {category.get('name')}: {e}")
                import traceback
                traceback.print_exc()
        
        # Затем создать остальные каналы
        other_channels = [ch for ch in channels_data if ch.get("type") != 4]
        # Сортировать по position
        other_channels.sort(key=lambda x: x.get("position", 0))
        
        for channel in other_channels:
            try:
                # Обновить parent_id если есть
                parent_id = channel.get("parent_id")
                if parent_id:
                    parent_id = int(parent_id) if isinstance(parent_id, (str, int)) else None
                    if parent_id and parent_id in channel_mapping:
                        parent_id = channel_mapping[parent_id]
                    else:
                        parent_id = None
                else:
                    parent_id = None
                
                channel_type = channel.get("type", 0)
                
                # Обновить permission_overwrites
                original_overwrites = channel.get("permission_overwrites", [])
                permission_overwrites = self.update_permission_overwrites(
                    original_overwrites,
                    role_mapping,
                    source_guild_id,
                    target_guild_id
                )
                
                # Отладочная информация
                if original_overwrites and not permission_overwrites:
                    print(f"    ⚠️ Внимание: у канала {channel.get('name')} были permissions, но они не были применены (возможно, роли не найдены)")
                
                # Подготовить параметры для создания канала
                channel_params = {
                    "guild_id": target_guild_id,
                    "name": channel.get("name", "channel"),
                    "type": channel_type,
                    "position": channel.get("position", 0)
                }
                
                # Добавить опциональные параметры
                if channel.get("topic"):
                    channel_params["topic"] = channel.get("topic")
                if channel.get("bitrate"):
                    channel_params["bitrate"] = channel.get("bitrate")
                if channel.get("user_limit"):
                    channel_params["user_limit"] = channel.get("user_limit")
                if channel.get("rate_limit_per_user"):
                    channel_params["rate_limit_per_user"] = channel.get("rate_limit_per_user")
                if parent_id:
                    channel_params["parent_id"] = parent_id
                if channel.get("nsfw") is not None:
                    channel_params["nsfw"] = channel.get("nsfw", False)
                
                # Добавить permission_overwrites только если они есть
                if permission_overwrites:
                    channel_params["permission_overwrites"] = permission_overwrites
                
                new_channel = await self.http.create_channel(**channel_params)
                channel_id = int(new_channel["id"])
                channel_mapping[int(channel["id"])] = channel_id
                
                # Если есть permissions, обновить их после создания (на случай если не применились)
                if permission_overwrites:
                    try:
                        await asyncio.sleep(0.2)  # Небольшая задержка перед обновлением
                        await self.http.modify_channel(
                            channel_id,
                            permission_overwrites=permission_overwrites
                        )
                        print(f"  ✅ Канал: {channel.get('name')} (тип: {channel_type}, permissions: {len(permission_overwrites)})")
                    except Exception as perm_error:
                        print(f"  ⚠️ Канал: {channel.get('name')} создан, но permissions не обновлены: {perm_error}")
                else:
                    print(f"  ✅ Канал: {channel.get('name')} (тип: {channel_type})")
                
                await asyncio.sleep(0.5)  # Задержка для rate limit
            except Exception as e:
                print(f"  ❌ Ошибка при создании канала {channel.get('name')}: {e}")
                import traceback
                traceback.print_exc()
        
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
    
    async def copy_emojis(self, source_guild_id: int, target_guild_id: int, emojis_data: List[Dict], role_mapping: Dict = None):
        """Скопировать эмодзи"""
        print(f"😀 Копирование эмодзи...")
        
        if role_mapping is None:
            role_mapping = {}
        
        for emoji in emojis_data:
            try:
                # Скачать эмодзи
                emoji_id = emoji.get("id")
                emoji_name = emoji.get("name")
                animated = emoji.get("animated", False)
                
                if not emoji_id or not emoji_name:
                    continue
                
                extension = "gif" if animated else "png"
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{extension}"
                
                emoji_data = await self.download_image(emoji_url)
                
                if emoji_data:
                    # Обновить роли эмодзи с учетом маппинга
                    emoji_roles = []
                    for role_id in emoji.get("roles", []):
                        role_id = int(role_id) if isinstance(role_id, str) else role_id
                        if role_id in role_mapping:
                            emoji_roles.append(str(role_mapping[role_id]))
                    
                    # Создать эмодзи
                    try:
                        result = await self.http.create_guild_emoji(
                            guild_id=target_guild_id,
                            name=emoji_name,
                            image=emoji_data,
                            roles=emoji_roles if emoji_roles else None
                        )
                        print(f"  ✅ Эмодзи: {emoji_name}")
                        await asyncio.sleep(2)  # Увеличена задержка для rate limit эмодзи
                    except Exception as emoji_error:
                        # Обработка специфичных ошибок
                        error_msg = str(emoji_error)
                        if "429" in error_msg or "rate limit" in error_msg.lower():
                            print(f"  ⚠️ Rate limit при создании эмодзи {emoji_name}, пропускаем...")
                            await asyncio.sleep(5)  # Дополнительная задержка при rate limit
                        else:
                            print(f"  ❌ Ошибка при создании эмодзи {emoji_name}: {emoji_error}")
            except Exception as e:
                print(f"  ❌ Ошибка при обработке эмодзи {emoji.get('name', 'unknown')}: {e}")
    
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
            
            # Скачать иконку если есть (если еще не была установлена при создании)
            icon_data = None
            if source_data.get("icon"):
                icon_url = f"https://cdn.discordapp.com/icons/{source_data['id']}/{source_data['icon']}.png"
                icon_data = await self.download_image(icon_url)
            
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
            
            # Подготовить данные для обновления
            update_data = {}
            
            # Название сервера
            if source_data.get("name"):
                update_data["name"] = source_data["name"]
            
            # Описание
            if source_data.get("description"):
                update_data["description"] = source_data["description"]
            
            # Иконка
            if icon_data:
                update_data["icon"] = icon_data
            
            # Баннер
            if banner_data:
                update_data["banner"] = banner_data
            
            # Splash
            if splash_data:
                update_data["splash"] = splash_data
            
            # Остальные настройки
            if source_data.get("verification_level") is not None:
                update_data["verification_level"] = source_data["verification_level"]
            if source_data.get("default_message_notifications") is not None:
                update_data["default_message_notifications"] = source_data["default_message_notifications"]
            if source_data.get("explicit_content_filter") is not None:
                update_data["explicit_content_filter"] = source_data["explicit_content_filter"]
            if afk_channel_id is not None:
                update_data["afk_channel_id"] = afk_channel_id
            if source_data.get("afk_timeout") is not None:
                update_data["afk_timeout"] = source_data["afk_timeout"]
            if system_channel_id is not None:
                update_data["system_channel_id"] = system_channel_id
            if source_data.get("system_channel_flags") is not None:
                update_data["system_channel_flags"] = source_data["system_channel_flags"]
            if rules_channel_id is not None:
                update_data["rules_channel_id"] = rules_channel_id
            if public_updates_channel_id is not None:
                update_data["public_updates_channel_id"] = public_updates_channel_id
            if source_data.get("preferred_locale"):
                update_data["preferred_locale"] = source_data["preferred_locale"]
            
            # Обновить гильдию
            if update_data:
                await self.http.modify_guild(
                    guild_id=target_guild_id,
                    **update_data
                )
                print(f"✅ Настройки сервера обновлены! (название: {update_data.get('name', 'не изменено')}, иконка: {'да' if icon_data else 'нет'})")
            else:
                print(f"⚠️ Нет данных для обновления настроек сервера")
        except Exception as e:
            print(f"❌ Ошибка при обновлении настроек: {e}")
            import traceback
            traceback.print_exc()
    
    async def clear_server(self, guild_id: int):
        """Очистить сервер: удалить все каналы, роли (кроме @everyone) и эмодзи"""
        print(f"🧹 Очистка сервера {guild_id}...")
        
        try:
            # Получить текущие данные сервера
            guild = await self.client.fetch_guild(guild_id)
            
            # Удалить все каналы
            print("  🗑️  Удаление каналов...")
            channels = await self.http.get_guild_channels(guild_id)
            for channel in channels:
                try:
                    await self.http.delete_channel(int(channel["id"]))
                    print(f"    ✅ Удален канал: {channel.get('name', 'unknown')}")
                    await asyncio.sleep(0.3)  # Задержка для rate limit
                except Exception as e:
                    print(f"    ❌ Ошибка при удалении канала {channel.get('name', 'unknown')}: {e}")
            
            # Удалить все эмодзи
            print("  🗑️  Удаление эмодзи...")
            emojis = await self.http.list_guild_emojis(guild_id)
            for emoji in emojis:
                try:
                    emoji_id = int(emoji["id"])
                    await self.http.delete_guild_emoji(guild_id, emoji_id)
                    print(f"    ✅ Удален эмодзи: {emoji.get('name', 'unknown')}")
                    await asyncio.sleep(0.3)  # Задержка для rate limit
                except Exception as e:
                    print(f"    ❌ Ошибка при удалении эмодзи {emoji.get('name', 'unknown')}: {e}")
            
            # Удалить все роли (кроме @everyone)
            print("  🗑️  Удаление ролей...")
            roles = await self.http.get_guild_roles(guild_id)
            # Отфильтровать @everyone роль и отсортировать по position (от меньшего к большему)
            # Удаляем от младших ролей к старшим, чтобы избежать проблем с иерархией
            roles_to_delete = [r for r in roles if int(r["id"]) != guild_id]
            roles_to_delete.sort(key=lambda x: x.get("position", 0))
            
            for role in roles_to_delete:
                role_id = int(role["id"])
                try:
                    await self.http.delete_guild_role(guild_id, role_id)
                    print(f"    ✅ Удалена роль: {role.get('name', 'unknown')} (position: {role.get('position', 0)})")
                    await asyncio.sleep(0.3)  # Задержка для rate limit
                except Exception as e:
                    print(f"    ❌ Ошибка при удалении роли {role.get('name', 'unknown')}: {e}")
            
            print(f"✅ Сервер {guild_id} очищен!")
        except Exception as e:
            print(f"❌ Ошибка при очистке сервера: {e}")
            import traceback
            traceback.print_exc()
    
    async def copy_server(self, from_guild_id: int, to_guild_id: Optional[int] = None, new_name: Optional[str] = None):
        """Скопировать сервер"""
        print(f"🚀 Начало копирования сервера {from_guild_id}...")
        
        # Получить данные исходного сервера
        source_data = await self.get_guild_data(from_guild_id)
        
        # Создать новый сервер или использовать существующий
        if to_guild_id:
            target_guild_id = to_guild_id
            print(f"📌 Использование существующего сервера {target_guild_id}")
            # Очистить существующий сервер перед копированием
            await self.clear_server(target_guild_id)
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
            source_data.get("emojis", []),
            role_mapping
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
    
    # Создать клиент с необходимыми intents для работы с серверами
    client = Client(
        token="MTQ0MzIzNzUyNTE0MDU0MTQ2MQ.Gq8rd-.ratCR_X2bK2gpNAwpMFCjiRNeRkMgrcBflipL8",
        intents=Intents.GUILDS | Intents.GUILD_MEMBERS | Intents.GUILD_EMOJIS_AND_STICKERS | 
                Intents.GUILD_INVITES | Intents.GUILD_WEBHOOKS | Intents.GUILD_VOICE_STATES
    )
    
    try:
        async with client:
            print(f"✅ Вход выполнен как {client.user}")
            
            copier = ServerCopier(client)
            await copier.copy_server(from_guild_id, to_guild_id, new_name)
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
