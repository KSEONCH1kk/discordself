"""Intents для Discord Gateway"""


class Intents:
    """Класс для работы с Discord Intents"""
    
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
    
    # Комбинации
    DEFAULT = GUILDS | GUILD_MEMBERS | GUILD_MODERATION | GUILD_EMOJIS_AND_STICKERS | GUILD_INTEGRATIONS | GUILD_WEBHOOKS | GUILD_INVITES | GUILD_VOICE_STATES | GUILD_PRESENCES | GUILD_MESSAGES | GUILD_MESSAGE_REACTIONS | GUILD_MESSAGE_TYPING | DIRECT_MESSAGES | DIRECT_MESSAGE_REACTIONS | DIRECT_MESSAGE_TYPING | MESSAGE_CONTENT
    
    ALL = 0xFFFFFFFF  # Все intents (может не работать для обычных ботов)
    
    @staticmethod
    def calculate(*intents):
        """Вычислить комбинацию intents"""
        result = 0
        for intent in intents:
            result |= intent
        return result

