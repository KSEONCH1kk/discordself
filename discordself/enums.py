"""Перечисления для Discord API.

Этот модуль содержит все перечисления (enums), используемые
в Discord API для типизации различных значений.
"""

from enum import IntEnum
from enum import Enum


class Status(str, Enum):
    """Статус пользователя Discord.
    
    Определяет статус присутствия пользователя в Discord.
    
    Attributes:
        ONLINE: Пользователь онлайн
        IDLE: Пользователь неактивен
        DND: Пользователь не беспокоить
        INVISIBLE: Пользователь невидим
        OFFLINE: Пользователь офлайн
    """
    ONLINE = "online"
    IDLE = "idle"
    DND = "dnd"
    INVISIBLE = "invisible"
    OFFLINE = "offline"


class ActivityType(IntEnum):
    """Тип активности пользователя.
    
    Определяет тип активности, отображаемой в профиле пользователя.
    
    Attributes:
        PLAYING: Играет в игру (0)
        STREAMING: Стримит (1)
        LISTENING: Слушает музыку (2)
        WATCHING: Смотрит (3)
        COMPETING: Участвует в соревновании (5)
    """
    PLAYING = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    COMPETING = 5


class ChannelType(IntEnum):
    """Тип канала Discord.
    
    Определяет тип канала в Discord.
    
    Attributes:
        GUILD_TEXT: Текстовый канал гильдии (0)
        DM: Прямое сообщение (1)
        GUILD_VOICE: Голосовой канал гильдии (2)
        GROUP_DM: Групповое DM (3)
        GUILD_CATEGORY: Категория каналов (4)
        GUILD_NEWS: Новостной канал (5)
        GUILD_STORE: Магазин гильдии (6)
        GUILD_NEWS_THREAD: Новостная нить (10)
        GUILD_PUBLIC_THREAD: Публичная нить (11)
        GUILD_PRIVATE_THREAD: Приватная нить (12)
        GUILD_STAGE_VOICE: Stage канал (13)
        GUILD_DIRECTORY: Директория (14)
        GUILD_FORUM: Форум (15)
    """
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_DIRECTORY = 14
    GUILD_FORUM = 15


class MessageType(IntEnum):
    """Тип сообщения Discord.
    
    Определяет тип сообщения в Discord.
    
    Attributes:
        DEFAULT: Обычное сообщение (0)
        RECIPIENT_ADD: Добавлен получатель (1)
        RECIPIENT_REMOVE: Удален получатель (2)
        CALL: Звонок (3)
        CHANNEL_NAME_CHANGE: Изменено имя канала (4)
        CHANNEL_ICON_CHANGE: Изменена иконка канала (5)
        CHANNEL_PINNED_MESSAGE: Закреплено сообщение (6)
        GUILD_MEMBER_JOIN: Присоединился участник (7)
        USER_PREMIUM_GUILD_SUBSCRIPTION: Подписка Nitro (8)
        USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1: Nitro Tier 1 (9)
        USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2: Nitro Tier 2 (10)
        USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3: Nitro Tier 3 (11)
        CHANNEL_FOLLOW_ADD: Подписка на канал (12)
        GUILD_DISCOVERY_DISQUALIFIED: Дискавери дисквалифицирован (14)
        GUILD_DISCOVERY_REQUALIFIED: Дискавери реквалифицирован (15)
        GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING: Предупреждение дискавери (16)
        GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING: Финальное предупреждение (17)
        THREAD_CREATED: Создана нить (18)
        REPLY: Ответ на сообщение (19)
        CHAT_INPUT_COMMAND: Slash команда (20)
        THREAD_STARTER_MESSAGE: Стартовое сообщение нити (21)
        GUILD_INVITE_REMINDER: Напоминание о приглашении (22)
        CONTEXT_MENU_COMMAND: Контекстная команда (23)
        AUTO_MODERATION_ACTION: Действие AutoMod (24)
    """
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PREMIUM_GUILD_SUBSCRIPTION = 8
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = 16
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = 17
    THREAD_CREATED = 18
    REPLY = 19
    CHAT_INPUT_COMMAND = 20
    THREAD_STARTER_MESSAGE = 21
    GUILD_INVITE_REMINDER = 22
    CONTEXT_MENU_COMMAND = 23
    AUTO_MODERATION_ACTION = 24


class GatewayOpcode(IntEnum):
    """Opcode для Discord Gateway протокола.
    
    Определяет тип операции в WebSocket сообщении Gateway.
    
    Attributes:
        DISPATCH: Событие от сервера (0)
        HEARTBEAT: Heartbeat от клиента (1)
        IDENTIFY: Идентификация клиента (2)
        PRESENCE_UPDATE: Обновление присутствия (3)
        VOICE_STATE_UPDATE: Обновление голосового состояния (4)
        RESUME: Возобновление сессии (6)
        RECONNECT: Переподключение (7)
        REQUEST_GUILD_MEMBERS: Запрос участников гильдии (8)
        INVALID_SESSION: Невалидная сессия (9)
        HELLO: Приветствие от сервера (10)
        HEARTBEAT_ACK: Подтверждение heartbeat (11)
    """
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


class InteractionType(IntEnum):
    """Тип interaction Discord.
    
    Определяет тип взаимодействия пользователя с ботом.
    
    Attributes:
        PING: Ping interaction (1)
        APPLICATION_COMMAND: Slash команда (2)
        MESSAGE_COMPONENT: Взаимодействие с компонентом (кнопка, меню) (3)
        APPLICATION_COMMAND_AUTOCOMPLETE: Автодополнение команды (4)
        MODAL_SUBMIT: Отправка модального окна (5)
    """
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class InteractionResponseType(IntEnum):
    """Тип ответа на interaction.
    
    Определяет тип ответа на interaction от бота.
    
    Attributes:
        PONG: Ответ на ping (1)
        CHANNEL_MESSAGE_WITH_SOURCE: Сообщение в канале (4)
        DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE: Отложенное сообщение (5)
        DEFERRED_UPDATE_MESSAGE: Отложенное обновление сообщения (6)
        UPDATE_MESSAGE: Обновление сообщения (7)
        APPLICATION_COMMAND_AUTOCOMPLETE_RESULT: Результат автодополнения (8)
        MODAL: Модальное окно (9)
    """
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9


class AutoModEventType(IntEnum):
    """Тип события AutoMod.
    
    Определяет, когда должно срабатывать правило AutoMod.
    
    Attributes:
        MESSAGE_SEND: При отправке сообщения (1)
    """
    MESSAGE_SEND = 1


class AutoModTriggerType(IntEnum):
    """Тип триггера AutoMod.
    
    Определяет условие срабатывания правила AutoMod.
    
    Attributes:
        KEYWORD: Триггер по ключевым словам (1)
        SPAM: Триггер по спаму (3)
        KEYWORD_PRESET: Триггер по пресету ключевых слов (4)
        MENTION_SPAM: Триггер по спаму упоминаний (5)
    """
    KEYWORD = 1
    SPAM = 3
    KEYWORD_PRESET = 4
    MENTION_SPAM = 5


class AutoModActionType(IntEnum):
    """Тип действия AutoMod.
    
    Определяет действие, которое выполняется при срабатывании правила.
    
    Attributes:
        BLOCK_MESSAGE: Заблокировать сообщение (1)
        SEND_ALERT_MESSAGE: Отправить предупреждение (2)
        TIMEOUT: Выдать таймаут пользователю (3)
    """
    BLOCK_MESSAGE = 1
    SEND_ALERT_MESSAGE = 2
    TIMEOUT = 3
