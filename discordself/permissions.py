"""Утилиты для работы с permissions Discord.

Этот модуль предоставляет классы и функции для работы
с правами доступа в Discord гильдиях.
"""

from typing import List, Set, Optional, Union
from enum import IntFlag


class Permissions(IntFlag):
    """Флаги permissions Discord.
    
    Представляет все возможные права доступа в Discord гильдиях.
    Используется для проверки и установки прав ролей и участников.
    
    Attributes:
        CREATE_INSTANT_INVITE: Создание приглашений (1 << 0)
        KICK_MEMBERS: Исключение участников (1 << 1)
        BAN_MEMBERS: Бан участников (1 << 2)
        ADMINISTRATOR: Администратор (все права) (1 << 3)
        MANAGE_CHANNELS: Управление каналами (1 << 4)
        MANAGE_GUILD: Управление гильдией (1 << 5)
        ADD_REACTIONS: Добавление реакций (1 << 6)
        VIEW_AUDIT_LOG: Просмотр журнала аудита (1 << 7)
        PRIORITY_SPEAKER: Приоритетный спикер (1 << 8)
        STREAM: Стрим (1 << 9)
        VIEW_CHANNEL: Просмотр канала (1 << 10)
        SEND_MESSAGES: Отправка сообщений (1 << 11)
        SEND_TTS_MESSAGES: Отправка TTS сообщений (1 << 12)
        MANAGE_MESSAGES: Управление сообщениями (1 << 13)
        EMBED_LINKS: Встраивание ссылок (1 << 14)
        ATTACH_FILES: Прикрепление файлов (1 << 15)
        READ_MESSAGE_HISTORY: Чтение истории сообщений (1 << 16)
        MENTION_EVERYONE: Упоминание @everyone (1 << 17)
        USE_EXTERNAL_EMOJIS: Использование внешних эмодзи (1 << 18)
        VIEW_GUILD_INSIGHTS: Просмотр аналитики гильдии (1 << 19)
        CONNECT: Подключение к голосовому каналу (1 << 20)
        SPEAK: Говорить в голосовом канале (1 << 21)
        MUTE_MEMBERS: Заглушение участников (1 << 22)
        DEAFEN_MEMBERS: Глушение участников (1 << 23)
        MOVE_MEMBERS: Перемещение участников (1 << 24)
        USE_VAD: Использование VAD (1 << 25)
        CHANGE_NICKNAME: Изменение своего ника (1 << 26)
        MANAGE_NICKNAMES: Управление никами (1 << 27)
        MANAGE_ROLES: Управление ролями (1 << 28)
        MANAGE_WEBHOOKS: Управление webhooks (1 << 29)
        MANAGE_EMOJIS_AND_STICKERS: Управление эмодзи и стикерами (1 << 30)
        USE_APPLICATION_COMMANDS: Использование команд приложения (1 << 31)
        REQUEST_TO_SPEAK: Запрос на выступление (1 << 32)
        MANAGE_EVENTS: Управление событиями (1 << 33)
        MANAGE_THREADS: Управление нитями (1 << 34)
        CREATE_PUBLIC_THREADS: Создание публичных нитей (1 << 35)
        CREATE_PRIVATE_THREADS: Создание приватных нитей (1 << 36)
        USE_EXTERNAL_STICKERS: Использование внешних стикеров (1 << 37)
        SEND_MESSAGES_IN_THREADS: Отправка сообщений в нитях (1 << 38)
        USE_EMBEDDED_ACTIVITIES: Использование встроенных активностей (1 << 39)
        MODERATE_MEMBERS: Модерация участников (1 << 40)
        VIEW_CREATOR_MONETIZATION_ANALYTICS: Просмотр аналитики монетизации (1 << 41)
        USE_SOUNDBOARD: Использование звуковой панели (1 << 42)
        CREATE_GUILD_EXPRESSIONS: Создание выражений гильдии (1 << 43)
        CREATE_EVENTS: Создание событий (1 << 44)
        USE_EXTERNAL_SOUNDS: Использование внешних звуков (1 << 45)
        SEND_VOICE_MESSAGES: Отправка голосовых сообщений (1 << 46)
    """
    # Общие permissions
    CREATE_INSTANT_INVITE = 1 << 0
    KICK_MEMBERS = 1 << 1
    BAN_MEMBERS = 1 << 2
    ADMINISTRATOR = 1 << 3
    MANAGE_CHANNELS = 1 << 4
    MANAGE_GUILD = 1 << 5
    ADD_REACTIONS = 1 << 6
    VIEW_AUDIT_LOG = 1 << 7
    PRIORITY_SPEAKER = 1 << 8
    STREAM = 1 << 9
    VIEW_CHANNEL = 1 << 10
    SEND_MESSAGES = 1 << 11
    SEND_TTS_MESSAGES = 1 << 12
    MANAGE_MESSAGES = 1 << 13
    EMBED_LINKS = 1 << 14
    ATTACH_FILES = 1 << 15
    READ_MESSAGE_HISTORY = 1 << 16
    MENTION_EVERYONE = 1 << 17
    USE_EXTERNAL_EMOJIS = 1 << 18
    VIEW_GUILD_INSIGHTS = 1 << 19
    CONNECT = 1 << 20
    SPEAK = 1 << 21
    MUTE_MEMBERS = 1 << 22
    DEAFEN_MEMBERS = 1 << 23
    MOVE_MEMBERS = 1 << 24
    USE_VAD = 1 << 25
    CHANGE_NICKNAME = 1 << 26
    MANAGE_NICKNAMES = 1 << 27
    MANAGE_ROLES = 1 << 28
    MANAGE_WEBHOOKS = 1 << 29
    MANAGE_EMOJIS_AND_STICKERS = 1 << 30
    USE_APPLICATION_COMMANDS = 1 << 31
    REQUEST_TO_SPEAK = 1 << 32
    MANAGE_EVENTS = 1 << 33
    MANAGE_THREADS = 1 << 34
    CREATE_PUBLIC_THREADS = 1 << 35
    CREATE_PRIVATE_THREADS = 1 << 36
    USE_EXTERNAL_STICKERS = 1 << 37
    SEND_MESSAGES_IN_THREADS = 1 << 38
    USE_EMBEDDED_ACTIVITIES = 1 << 39
    MODERATE_MEMBERS = 1 << 40
    VIEW_CREATOR_MONETIZATION_ANALYTICS = 1 << 41
    USE_SOUNDBOARD = 1 << 42
    CREATE_GUILD_EXPRESSIONS = 1 << 43
    CREATE_EVENTS = 1 << 44
    USE_EXTERNAL_SOUNDS = 1 << 45
    SEND_VOICE_MESSAGES = 1 << 46


class PermissionCalculator:
    """Калькулятор для работы с permissions Discord.
    
    Предоставляет статические методы для преобразования, проверки
    и вычисления прав доступа в Discord гильдиях.
    """
    
    @staticmethod
    def from_value(value: Union[int, str]) -> Permissions:
        """Создать Permissions из числового значения.
        
        Args:
            value: Числовое значение прав (int или str)
        
        Returns:
            Permissions: Объект Permissions
        """
        if isinstance(value, str):
            value = int(value)
        return Permissions(value)
    
    @staticmethod
    def to_value(permissions: Permissions) -> int:
        """Преобразовать Permissions в числовое значение.
        
        Args:
            permissions: Объект Permissions
        
        Returns:
            int: Числовое значение прав
        """
        return int(permissions)
    
    @staticmethod
    def has_permission(permissions: Union[int, str, Permissions], permission: Permissions) -> bool:
        """Проверить наличие конкретного permission.
        
        Args:
            permissions: Права для проверки (int, str или Permissions)
            permission: Право для проверки
        
        Returns:
            bool: True если право есть (или есть ADMINISTRATOR), False иначе
        """
        if isinstance(permissions, (int, str)):
            permissions = PermissionCalculator.from_value(permissions)
        
        # ADMINISTRATOR дает все права
        if Permissions.ADMINISTRATOR in permissions:
            return True
        
        return permission in permissions
    
    @staticmethod
    def has_any_permission(permissions: Union[int, str, Permissions], *permission_list: Permissions) -> bool:
        """Проверить наличие хотя бы одного permission.
        
        Args:
            permissions: Права для проверки (int, str или Permissions)
            *permission_list: Список прав для проверки
        
        Returns:
            bool: True если есть хотя бы одно право, False иначе
        """
        if isinstance(permissions, (int, str)):
            permissions = PermissionCalculator.from_value(permissions)
        
        # ADMINISTRATOR дает все права
        if Permissions.ADMINISTRATOR in permissions:
            return True
        
        return any(perm in permissions for perm in permission_list)
    
    @staticmethod
    def has_all_permissions(permissions: Union[int, str, Permissions], *permission_list: Permissions) -> bool:
        """Проверить наличие всех permissions.
        
        Args:
            permissions: Права для проверки (int, str или Permissions)
            *permission_list: Список прав для проверки
        
        Returns:
            bool: True если есть все права, False иначе
        """
        if isinstance(permissions, (int, str)):
            permissions = PermissionCalculator.from_value(permissions)
        
        # ADMINISTRATOR дает все права
        if Permissions.ADMINISTRATOR in permissions:
            return True
        
        return all(perm in permissions for perm in permission_list)
    
    @staticmethod
    def add_permission(permissions: Union[int, str, Permissions], permission: Permissions) -> Permissions:
        """Добавить permission к существующим правам.
        
        Args:
            permissions: Текущие права (int, str или Permissions)
            permission: Право для добавления
        
        Returns:
            Permissions: Новые права с добавленным правом
        """
        if isinstance(permissions, (int, str)):
            permissions = PermissionCalculator.from_value(permissions)
        return permissions | permission
    
    @staticmethod
    def remove_permission(permissions: Union[int, str, Permissions], permission: Permissions) -> Permissions:
        """Удалить permission из существующих прав.
        
        Args:
            permissions: Текущие права (int, str или Permissions)
            permission: Право для удаления
        
        Returns:
            Permissions: Новые права без удаленного права
        """
        if isinstance(permissions, (int, str)):
            permissions = PermissionCalculator.from_value(permissions)
        return permissions & ~permission
    
    @staticmethod
    def toggle_permission(permissions: Union[int, str, Permissions], permission: Permissions) -> Permissions:
        """Переключить permission (добавить если нет, удалить если есть).
        
        Args:
            permissions: Текущие права (int, str или Permissions)
            permission: Право для переключения
        
        Returns:
            Permissions: Новые права с переключенным правом
        """
        if isinstance(permissions, (int, str)):
            permissions = PermissionCalculator.from_value(permissions)
        return permissions ^ permission
    
    @staticmethod
    def get_permission_list(permissions: Union[int, str, Permissions]) -> List[str]:
        """Получить список всех активных permissions.
        
        Args:
            permissions: Права для анализа (int, str или Permissions)
        
        Returns:
            List[str]: Список названий активных прав
        """
        if isinstance(permissions, (int, str)):
            permissions = PermissionCalculator.from_value(permissions)
        
        result = []
        for perm in Permissions:
            if perm in permissions:
                result.append(perm.name)
        return result
    
    @staticmethod
    def calculate_overwrite(base: Union[int, str, Permissions], allow: Union[int, str, Permissions], deny: Union[int, str, Permissions]) -> Permissions:
        """Вычислить итоговые permissions с учетом overwrites.
        
        Вычисляет итоговые права на основе базовых прав, разрешенных
        и запрещенных прав из overwrites канала.
        
        Args:
            base: Базовые права (int, str или Permissions)
            allow: Разрешенные права из overwrite (int, str или Permissions)
            deny: Запрещенные права из overwrite (int, str или Permissions)
        
        Returns:
            Permissions: Итоговые права
        """
        if isinstance(base, (int, str)):
            base = PermissionCalculator.from_value(base)
        if isinstance(allow, (int, str)):
            allow = PermissionCalculator.from_value(allow)
        if isinstance(deny, (int, str)):
            deny = PermissionCalculator.from_value(deny)
        
        # Формула: (base & ~deny) | allow
        return (base & ~deny) | allow
    
    @staticmethod
    def calculate_role_permissions(
        guild_permissions: Union[int, str, Permissions],
        role_permissions: List[Union[int, str, Permissions]],
        role_positions: Optional[List[int]] = None
    ) -> Permissions:
        """Вычислить итоговые permissions из ролей"""
        if isinstance(guild_permissions, (int, str)):
            guild_permissions = PermissionCalculator.from_value(guild_permissions)
        
        result = guild_permissions
        
        # Если есть позиции ролей, сортируем по позиции (от большей к меньшей)
        if role_positions and len(role_positions) == len(role_permissions):
            sorted_roles = sorted(
                zip(role_permissions, role_positions),
                key=lambda x: x[1],
                reverse=True
            )
            role_permissions = [r[0] for r in sorted_roles]
        
        # Объединяем permissions всех ролей
        for role_perm in role_permissions:
            if isinstance(role_perm, (int, str)):
                role_perm = PermissionCalculator.from_value(role_perm)
            result |= role_perm
        
        return result
    
    @staticmethod
    def get_text_permissions() -> Set[Permissions]:
        """Получить набор permissions для текстовых каналов"""
        return {
            Permissions.VIEW_CHANNEL,
            Permissions.SEND_MESSAGES,
            Permissions.SEND_TTS_MESSAGES,
            Permissions.MANAGE_MESSAGES,
            Permissions.EMBED_LINKS,
            Permissions.ATTACH_FILES,
            Permissions.READ_MESSAGE_HISTORY,
            Permissions.MENTION_EVERYONE,
            Permissions.USE_EXTERNAL_EMOJIS,
            Permissions.ADD_REACTIONS,
            Permissions.MANAGE_THREADS,
            Permissions.CREATE_PUBLIC_THREADS,
            Permissions.CREATE_PRIVATE_THREADS,
            Permissions.SEND_MESSAGES_IN_THREADS,
        }
    
    @staticmethod
    def get_voice_permissions() -> Set[Permissions]:
        """Получить набор permissions для голосовых каналов"""
        return {
            Permissions.VIEW_CHANNEL,
            Permissions.CONNECT,
            Permissions.SPEAK,
            Permissions.STREAM,
            Permissions.USE_VAD,
            Permissions.MUTE_MEMBERS,
            Permissions.DEAFEN_MEMBERS,
            Permissions.MOVE_MEMBERS,
            Permissions.USE_EXTERNAL_SOUNDS,
            Permissions.SEND_VOICE_MESSAGES,
        }
    
    @staticmethod
    def get_moderation_permissions() -> Set[Permissions]:
        """Получить набор permissions для модерации"""
        return {
            Permissions.KICK_MEMBERS,
            Permissions.BAN_MEMBERS,
            Permissions.MANAGE_MESSAGES,
            Permissions.MANAGE_CHANNELS,
            Permissions.MANAGE_ROLES,
            Permissions.MANAGE_GUILD,
            Permissions.VIEW_AUDIT_LOG,
            Permissions.MODERATE_MEMBERS,
        }


# Удобные функции
def has_permission(permissions: Union[int, str, Permissions], permission: Permissions) -> bool:
    """Проверить наличие permission"""
    return PermissionCalculator.has_permission(permissions, permission)


def has_any_permission(permissions: Union[int, str, Permissions], *permission_list: Permissions) -> bool:
    """Проверить наличие хотя бы одного permission"""
    return PermissionCalculator.has_any_permission(permissions, *permission_list)


def has_all_permissions(permissions: Union[int, str, Permissions], *permission_list: Permissions) -> bool:
    """Проверить наличие всех permissions"""
    return PermissionCalculator.has_all_permissions(permissions, *permission_list)

