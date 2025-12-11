"""Intents для Discord Gateway.

Intents определяют, какие события Discord Gateway будет отправлять клиенту.
Этот модуль предоставляет константы и методы для работы с intents.
"""


class Intents:
    """Класс для работы с Discord Gateway Intents.
    
    Intents - это битовые флаги, которые определяют, какие события
    Discord будет отправлять вашему клиенту. Используйте их для
    оптимизации трафика и производительности.
    
    Attributes:
        GUILDS: События гильдий (guild create/update/delete)
        GUILD_MEMBERS: События участников гильдий
        GUILD_MODERATION: События модерации (bans, kicks)
        GUILD_EMOJIS_AND_STICKERS: События эмодзи и стикеров
        GUILD_INTEGRATIONS: События интеграций
        GUILD_WEBHOOKS: События webhooks
        GUILD_INVITES: События приглашений
        GUILD_VOICE_STATES: События голосовых состояний
        GUILD_PRESENCES: События присутствия пользователей
        GUILD_MESSAGES: События сообщений в гильдиях
        GUILD_MESSAGE_REACTIONS: События реакций на сообщения
        GUILD_MESSAGE_TYPING: События печати в гильдиях
        DIRECT_MESSAGES: События прямых сообщений
        DIRECT_MESSAGE_REACTIONS: События реакций в DM
        DIRECT_MESSAGE_TYPING: События печати в DM
        MESSAGE_CONTENT: Доступ к содержимому сообщений
        GUILD_SCHEDULED_EVENTS: События запланированных событий
        AUTO_MODERATION_CONFIGURATION: События конфигурации AutoMod
        AUTO_MODERATION_EXECUTION: События выполнения AutoMod
        GUILD_MESSAGE_POLLS: События опросов в гильдиях
        DIRECT_MESSAGE_POLLS: События опросов в DM
    
    Example:
        ```python
        intents = Intents.GUILD_MESSAGES | Intents.MESSAGE_CONTENT
        client = Client(token="...", intents=intents)
        ```
    """
    
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_MODERATION = 1 << 2
    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    MESSAGE_CONTENT = 1 << 15
    GUILD_SCHEDULED_EVENTS = 1 << 16
    AUTO_MODERATION_CONFIGURATION = 1 << 20
    AUTO_MODERATION_EXECUTION = 1 << 21
    GUILD_MESSAGE_POLLS = 1 << 24
    DIRECT_MESSAGE_POLLS = 1 << 25
    
    DEFAULT = GUILDS | GUILD_MEMBERS | GUILD_MODERATION | GUILD_EMOJIS_AND_STICKERS | GUILD_INTEGRATIONS | GUILD_WEBHOOKS | GUILD_INVITES | GUILD_VOICE_STATES | GUILD_PRESENCES | GUILD_MESSAGES | GUILD_MESSAGE_REACTIONS | GUILD_MESSAGE_TYPING | DIRECT_MESSAGES | DIRECT_MESSAGE_REACTIONS | DIRECT_MESSAGE_TYPING | MESSAGE_CONTENT
    
    ALL = 0xFFFFFFFF
    
    @staticmethod
    def calculate(*intents):
        """Вычислить комбинацию intents.
        
        Объединяет несколько intents в одну битовую маску.
        
        Args:
            *intents: Intents для объединения
        
        Returns:
            int: Комбинированная битовая маска intents
        
        Example:
            ```python
            intents = Intents.calculate(
                Intents.GUILD_MESSAGES,
                Intents.MESSAGE_CONTENT
            )
            ```
        """
        result = 0
        for intent in intents:
            result |= intent
        return result

