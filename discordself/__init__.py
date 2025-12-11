"""Discord Selfbot Library - Полнофункциональная библиотека для Discord selfbot.

Этот пакет предоставляет полнофункциональную библиотеку для создания
Discord selfbot приложений с поддержкой всех основных функций Discord API.

Основные компоненты:
    - Client: Основной класс для работы с Discord
    - Models: Модели данных Discord (User, Guild, Channel, Message и т.д.)
    - Commands: Система команд для ботов
    - Voice: Поддержка голосовых каналов
    - Embeds: Создание красивых embed сообщений
    - Webhooks: Работа с webhooks
    - Intents: Управление Gateway intents
    - Exceptions: Исключения библиотеки

Example:
    ```python
    from discordself import Client, Intents
    
    client = Client(token="YOUR_TOKEN", intents=Intents.GUILD_MESSAGES)
    
    @client.event("ready")
    async def on_ready():
        print(f"Logged in as {client.user}")
    
    @client.event("message_create")
    async def on_message(message):
        if message.content == "!hello":
            await message.channel.send("Hello!")
    
    client.run()
    ```

Warning:
    Использование selfbot нарушает Terms of Service Discord.
    Используйте на свой риск.
"""

from .client import Client
from .models import User, Guild, Channel, Message, Member, Role, Emoji, VoiceState, Interaction, AutoModAction, AutoModRule, Attachment, Invite, Integration, StageInstance, ScheduledEvent
from .enums import Status, ActivityType, InteractionType, InteractionResponseType, AutoModEventType, AutoModTriggerType, AutoModActionType
from .embeds import Embed, Button, SelectMenu, ActionRow, create_embed, create_button, create_select_menu, create_action_row
from .webhook import Webhook
from .intents import Intents
from .exceptions import (
    DiscordException,
    HTTPException,
    RateLimitException,
    WebSocketException,
    LoginFailure,
    Forbidden,
    NotFound,
    BadRequest,
    Unauthorized,
    CommandError,
    CommandNotFound,
    MissingRequiredArgument,
    BadArgument,
    CheckFailure,
    MissingPermissions,
    BotMissingPermissions,
    NoPrivateMessage,
    PrivateMessageOnly,
    CommandOnCooldown
)
from .commands import (
    Command,
    CommandGroup,
    Bot,
    Context,
    Converter,
    MemberConverter,
    UserConverter,
    ChannelConverter,
    RoleConverter,
    EmojiConverter,
    IntConverter,
    FloatConverter,
    BoolConverter,
    Greedy,
    Literal
)
from .cogs import (
    Cog,
    CogManager,
    command,
    group,
    listener
)
from .checks import (
    check,
    has_permissions,
    bot_has_permissions,
    has_role,
    has_any_role,
    is_owner,
    is_nsfw,
    guild_only,
    dm_only,
    cooldown
)
from .permissions import (
    Permissions,
    PermissionCalculator,
    has_permission,
    has_any_permission,
    has_all_permissions
)
from .voice import (
    VoiceState,
    VoiceClient,
    connect_to_voice
)
from .audio_source import (
    AudioSource,
    PCMAudioSource,
    OpusAudioSource,
    FileAudioSource,
    BytesAudioSource,
    SilenceSource,
    VolumeTransformer,
    AudioFilter,
    LowPassFilter,
    FilteredAudioSource
)
from .ffmpeg import (
    FFmpegPCMAudio,
    FFmpegOpusAudio
)
from .youtube import (
    YouTubeSource,
    URLSource,
    create_yt_source,
    create_url_source
)
from .recording import (
    AudioSink,
    FileSink,
    PCMFileSink,
    RecordingVoiceClient
)
from .help import (
    HelpCommand,
    DefaultHelpCommand,
    setup_help_command
)
from .tasks import (
    Loop,
    loop
)
from .views import (
    View,
    ButtonView,
    SelectMenuView,
    button
)

__version__ = "1.0.0"
__author__ = "DiscordSelf"

__all__ = [
    # Client
    'Client',
    # Models
    'User',
    'Guild',
    'Channel',
    'Message',
    'Member',
    'Role',
    'Emoji',
    'VoiceState',
    'Interaction',
    'AutoModAction',
    'AutoModRule',
    'Attachment',
    'Invite',
    'Integration',
    'StageInstance',
    'ScheduledEvent',
    # Enums
    'Status',
    'ActivityType',
    'InteractionType',
    'InteractionResponseType',
    'AutoModEventType',
    'AutoModTriggerType',
    'AutoModActionType',
    # Embeds
    'Embed',
    'Button',
    'SelectMenu',
    'ActionRow',
    'create_embed',
    'create_button',
    'create_select_menu',
    'create_action_row',
    # Webhook
    'Webhook',
    # Intents
    'Intents',
    # Exceptions
    'DiscordException',
    'HTTPException',
    'RateLimitException',
    'WebSocketException',
    'LoginFailure',
    'Forbidden',
    'NotFound',
    'BadRequest',
    'Unauthorized',
    'CommandError',
    'CommandNotFound',
    'MissingRequiredArgument',
    'BadArgument',
    'CheckFailure',
    'MissingPermissions',
    'BotMissingPermissions',
    'NoPrivateMessage',
    'PrivateMessageOnly',
    # Commands
    'Command',
    'CommandGroup',
    'Bot',
    'Context',
    'Converter',
    'MemberConverter',
    'UserConverter',
    'ChannelConverter',
    'RoleConverter',
    'EmojiConverter',
    'IntConverter',
    'FloatConverter',
    'BoolConverter',
    'Greedy',
    'Literal',
    # Cogs
    'Cog',
    'CogManager',
    'command',
    'group',
    'listener',
    # Checks
    'check',
    'has_permissions',
    'bot_has_permissions',
    'has_role',
    'has_any_role',
    'is_owner',
    'is_nsfw',
    'guild_only',
    'dm_only',
    'cooldown',
    # Permissions
    'Permissions',
    'PermissionCalculator',
    'has_permission',
    'has_any_permission',
    'has_all_permissions',
    # Voice
    'VoiceState',
    'VoiceClient',
    'connect_to_voice',
    # Audio Sources
    'AudioSource',
    'PCMAudioSource',
    'OpusAudioSource',
    'FileAudioSource',
    'BytesAudioSource',
    'SilenceSource',
    'VolumeTransformer',
    'AudioFilter',
    'LowPassFilter',
    'FilteredAudioSource',
    # FFmpeg
    'FFmpegPCMAudio',
    'FFmpegOpusAudio',
    # YouTube/URL
    'YouTubeSource',
    'URLSource',
    'create_yt_source',
    'create_url_source',
    # Recording
    'AudioSink',
    'FileSink',
    'PCMFileSink',
    'RecordingVoiceClient',
    # Help
    'HelpCommand',
    'DefaultHelpCommand',
    'setup_help_command',
    # Tasks
    'Loop',
    'loop',
    # Views
    'View',
    'ButtonView',
    'SelectMenuView',
    'button',
]

