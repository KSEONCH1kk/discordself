"""Система команд для Discord Selfbot"""

import asyncio
import inspect
import re
from typing import Optional, Dict, List, Callable, Any, Union, Type
from .exceptions import (
    CommandError, CommandNotFound, MissingRequiredArgument,
    BadArgument, CheckFailure, CommandOnCooldown
)
from .models import Message, User, Member, Guild, Channel, Role, Emoji


class Context:
    """Контекст выполнения команды"""
    
    def __init__(self, message: Message, command: 'Command', prefix: str, args: List[str], kwargs: Dict[str, Any], bot: Optional['Bot'] = None):
        self.message = message
        self.command = command
        self.prefix = prefix
        self.args = args
        self.kwargs = kwargs
        self.bot = bot or (message._client if message._client else None)
        
        # Удобные атрибуты
        self.author = message.author
        self.channel = message.channel
        self.guild = message.guild
        # Получить user из bot (может быть Bot или Client)
        if self.bot:
            if hasattr(self.bot, 'user'):
                self.me = self.bot.user
            elif hasattr(self.bot, 'client') and hasattr(self.bot.client, 'user'):
                self.me = self.bot.client.user
            else:
                self.me = None
        else:
            self.me = None
        
    async def send(self, content: Optional[str] = None, embed: Optional[Any] = None, embeds: Optional[list] = None, **kwargs):
        """Отправить сообщение в канал"""
        if self.channel:
            # Преобразовать embed в embeds если нужно
            if embed and not embeds:
                embeds = [embed]
            # Преобразовать embed объекты в словари и отфильтровать пустые
            if embeds:
                embeds_dicts = []
                for e in embeds:
                    if hasattr(e, 'to_dict'):
                        e_dict = e.to_dict()
                        # Проверить, что embed не пустой (должен иметь хотя бы title, description, fields, или другой контент)
                        if e_dict and (e_dict.get('title') or e_dict.get('description') or e_dict.get('fields') or e_dict.get('image') or e_dict.get('thumbnail')):
                            embeds_dicts.append(e_dict)
                    else:
                        embeds_dicts.append(e)
                embeds = embeds_dicts if embeds_dicts else None
            
            # Убедиться, что есть либо content, либо embeds (Discord требует хотя бы одно)
            if not content and (not embeds or len(embeds) == 0):
                content = "\u200b"  # Zero-width space как fallback
            
            # Передать embeds, если они есть
            if embeds:
                return await self.channel.send(content=content if content else None, embeds=embeds, **kwargs)
            else:
                return await self.channel.send(content=content if content else None, **kwargs)
        raise RuntimeError("Cannot send message: channel is None")
    
    async def reply(self, content: Optional[str] = None, **kwargs):
        """Ответить на сообщение"""
        if self.message:
            kwargs.setdefault('message_reference', {
                'message_id': self.message.id,
                'channel_id': self.message.channel_id,
                'guild_id': self.guild.id if self.guild else None
            })
        return await self.send(content, **kwargs)


class Converter:
    """Базовый класс для конвертеров аргументов"""
    
    async def convert(self, ctx: Context, argument: str) -> Any:
        """Конвертировать аргумент"""
        raise NotImplementedError("Converter must implement convert() method")


class MemberConverter(Converter):
    """Конвертер для Member"""
    
    async def convert(self, ctx: Context, argument: str) -> Optional[Member]:
        if not ctx.guild:
            return None
        
        # Попытка найти по ID
        if argument.isdigit():
            member_id = int(argument)
            # Здесь нужно получить member из guild
            # Упрощенная версия
            return None
        
        # Попытка найти по упоминанию
        mention_match = re.match(r'<@!?(\d+)>', argument)
        if mention_match:
            member_id = int(mention_match.group(1))
            # Здесь нужно получить member из guild
            return None
        
        return None


class UserConverter(Converter):
    """Конвертер для User"""
    
    async def convert(self, ctx: Context, argument: str) -> Optional[User]:
        # Попытка найти по ID
        if argument.isdigit():
            user_id = int(argument)
            if ctx.bot:
                return ctx.bot.get_user(user_id)
        
        # Попытка найти по упоминанию
        mention_match = re.match(r'<@!?(\d+)>', argument)
        if mention_match:
            user_id = int(mention_match.group(1))
            if ctx.bot:
                return ctx.bot.get_user(user_id)
        
        return None


class ChannelConverter(Converter):
    """Конвертер для Channel"""
    
    async def convert(self, ctx: Context, argument: str) -> Optional[Channel]:
        if not ctx.guild:
            return None
        
        # Попытка найти по ID
        if argument.isdigit():
            channel_id = int(argument)
            if ctx.bot:
                return ctx.bot.get_channel(channel_id)
        
        # Попытка найти по упоминанию
        mention_match = re.match(r'<#(\d+)>', argument)
        if mention_match:
            channel_id = int(mention_match.group(1))
            if ctx.bot:
                return ctx.bot.get_channel(channel_id)
        
        return None


class RoleConverter(Converter):
    """Конвертер для Role"""
    
    async def convert(self, ctx: Context, argument: str) -> Optional[Role]:
        if not ctx.guild:
            raise BadArgument("Cannot get role outside of a guild")
        
        # Попытка найти по ID
        if argument.isdigit():
            role_id = int(argument)
            if ctx.guild.roles:
                for role in ctx.guild.roles:
                    if role.id == role_id:
                        return role
        
        # Попытка найти по упоминанию
        mention_match = re.match(r'<@&(\d+)>', argument)
        if mention_match:
            role_id = int(mention_match.group(1))
            if ctx.guild.roles:
                for role in ctx.guild.roles:
                    if role.id == role_id:
                        return role
        
        # Попытка найти по имени
        if ctx.guild.roles:
            for role in ctx.guild.roles:
                if role.name.lower() == argument.lower():
                    return role
        
        raise BadArgument(f"Role '{argument}' not found")


class EmojiConverter(Converter):
    """Конвертер для Emoji"""
    
    async def convert(self, ctx: Context, argument: str) -> Optional[Emoji]:
        # Попытка найти по ID (custom emoji)
        emoji_match = re.match(r'<a?:(\w+):(\d+)>', argument)
        if emoji_match:
            emoji_id = int(emoji_match.group(2))
            if ctx.guild and ctx.guild.emojis:
                for emoji in ctx.guild.emojis:
                    if emoji.id == emoji_id:
                        return emoji
        
        # Попытка найти по имени
        if ctx.guild and ctx.guild.emojis:
            for emoji in ctx.guild.emojis:
                if emoji.name.lower() == argument.lower():
                    return emoji
        
        # Unicode emoji (просто возвращаем строку)
        # Можно вернуть специальный объект для unicode emoji
        return None


class Greedy:
    """Конвертер для множества аргументов"""
    
    def __init__(self, converter: Type[Converter] = None):
        self.converter = converter
    
    async def convert(self, ctx: Context, argument: str) -> Any:
        if self.converter:
            converter_instance = self.converter()
            return await converter_instance.convert(ctx, argument)
        return argument


class Literal:
    """Конвертер для литеральных значений"""
    
    def __init__(self, *values: str):
        self.values = values
    
    async def convert(self, ctx: Context, argument: str) -> str:
        if argument not in self.values:
            raise BadArgument(f"'{argument}' must be one of: {', '.join(self.values)}")
        return argument


class IntConverter(Converter):
    """Конвертер для int"""
    
    async def convert(self, ctx: Context, argument: str) -> int:
        try:
            return int(argument)
        except ValueError:
            raise BadArgument(f"'{argument}' is not a valid integer")


class FloatConverter(Converter):
    """Конвертер для float"""
    
    async def convert(self, ctx: Context, argument: str) -> float:
        try:
            return float(argument)
        except ValueError:
            raise BadArgument(f"'{argument}' is not a valid float")


class BoolConverter(Converter):
    """Конвертер для bool"""
    
    async def convert(self, ctx: Context, argument: str) -> bool:
        lower = argument.lower()
        if lower in ('true', 'yes', '1', 'on', 'enable'):
            return True
        elif lower in ('false', 'no', '0', 'off', 'disable'):
            return False
        raise BadArgument(f"'{argument}' is not a valid boolean")


# Регистр конвертеров по типам
CONVERTERS: Dict[Type, Type[Converter]] = {
    int: IntConverter,
    float: FloatConverter,
    bool: BoolConverter,
    str: None,  # Строка не требует конвертации
    Member: MemberConverter,
    User: UserConverter,
    Channel: ChannelConverter,
    Role: RoleConverter,
    Emoji: EmojiConverter,
}


class Command:
    """Класс команды"""
    
    def __init__(
        self,
        func: Callable,
        name: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        description: Optional[str] = None,
        help: Optional[str] = None,
        checks: Optional[List[Callable]] = None,
        **kwargs
    ):
        self.callback = func
        self.name = name or func.__name__
        self.aliases = aliases or []
        self.description = description or func.__doc__ or "No description"
        self.help = help or self.description
        self.checks = checks or []
        self.enabled = kwargs.get('enabled', True)
        self.hidden = kwargs.get('hidden', False)
        # Получить cooldown из kwargs или из атрибута функции
        self.cooldown = kwargs.get('cooldown', None) or getattr(func, '__cooldown__', None)
        self._cooldown_buckets: Dict[str, List[float]] = {}
        
        # Парсинг сигнатуры функции
        self.signature = inspect.signature(func)
        self.params = list(self.signature.parameters.values())[1:]  # Пропускаем ctx
        
    async def can_run(self, ctx: Context) -> bool:
        """Проверить, может ли команда быть выполнена"""
        # Проверки
        for check in self.checks:
            try:
                if asyncio.iscoroutinefunction(check):
                    result = await check(ctx)
                else:
                    result = check(ctx)
                if not result:
                    return False
            except Exception:
                return False
        return True
    
    def _get_cooldown_key(self, ctx: Context) -> str:
        """Получить ключ для cooldown bucket"""
        if not self.cooldown:
            return None
        
        rate, per, cooldown_type = self.cooldown
        # type: 1 = per user, 2 = per guild, 3 = per channel, 4 = global
        if cooldown_type == 1:  # per user
            return f"{self.name}:user:{ctx.author.id}"
        elif cooldown_type == 2:  # per guild
            return f"{self.name}:guild:{ctx.guild.id if ctx.guild else 0}"
        elif cooldown_type == 3:  # per channel
            return f"{self.name}:channel:{ctx.channel.id if ctx.channel else 0}"
        else:  # global
            return f"{self.name}:global"
    
    async def invoke(self, ctx: Context, *args, **kwargs):
        """Вызвать команду"""
        print(f"🔵 Command.invoke called for '{self.name}'")
        # Проверки
        if not await self.can_run(ctx):
            print(f"❌ Check failed for command '{self.name}'")
            raise CheckFailure(f"Check failed for command {self.name}")
        
        print(f"🔵 Command '{self.name}' can run, checking cooldown...")
        print(f"🔵 Command '{self.name}' cooldown: {self.cooldown}")
        # Cooldown проверка
        if self.cooldown:
            import time
            key = self._get_cooldown_key(ctx)
            print(f"🔵 Cooldown key: {key}")
            if key:
                rate, per, _ = self.cooldown
                now = time.time()
                
                if key not in self._cooldown_buckets:
                    self._cooldown_buckets[key] = []
                
                # Удалить старые записи
                self._cooldown_buckets[key] = [
                    t for t in self._cooldown_buckets[key] if now - t < per
                ]
                
                print(f"🔵 Cooldown bucket for '{key}': {len(self._cooldown_buckets[key])}/{rate} uses")
                
                # Проверить лимит
                if len(self._cooldown_buckets[key]) >= rate:
                    retry_after = per - (now - self._cooldown_buckets[key][0])
                    print(f"❌ Command '{self.name}' on cooldown! Retry after {retry_after:.2f}s")
                    from .exceptions import CommandOnCooldown
                    raise CommandOnCooldown(self, retry_after)
                
                # Добавить текущее время
                self._cooldown_buckets[key].append(now)
                print(f"🔵 Added cooldown entry for '{key}', now {len(self._cooldown_buckets[key])}/{rate} uses")
        
        # Вызов команды
        print(f"🔵 Calling command callback '{self.name}'...")
        if asyncio.iscoroutinefunction(self.callback):
            result = await self.callback(ctx, *args, **kwargs)
            print(f"🔵 Command callback '{self.name}' returned: {result}")
            return result
        else:
            result = self.callback(ctx, *args, **kwargs)
            print(f"🔵 Command callback '{self.name}' returned: {result}")
            return result
    
    async def prepare(self, ctx: Context, args: List[str]) -> tuple:
        """Подготовить аргументы для команды"""
        converted_args = []
        converted_kwargs = {}
        
        param_iter = iter(self.params)
        arg_iter = iter(args)
        
        for param in param_iter:
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                # *args
                converted_args.extend(await self._convert_args(ctx, list(arg_iter), param))
                break
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                # **kwargs - не поддерживается в командах
                continue
            elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                # keyword-only параметры
                if param.default == inspect.Parameter.empty:
                    raise MissingRequiredArgument(param.name)
                converted_kwargs[param.name] = param.default
            else:
                # Обычный параметр
                try:
                    arg = next(arg_iter)
                except StopIteration:
                    if param.default == inspect.Parameter.empty:
                        raise MissingRequiredArgument(param.name)
                    converted_args.append(param.default)
                    continue
                
                # Конвертация
                converted = await self._convert_argument(ctx, arg, param)
                converted_args.append(converted)
        
        return tuple(converted_args), converted_kwargs
    
    async def _convert_argument(self, ctx: Context, argument: str, param: inspect.Parameter) -> Any:
        """Конвертировать один аргумент"""
        param_type = param.annotation
        
        # Если тип не указан, возвращаем строку
        if param_type == inspect.Parameter.empty:
            return argument
        
        # Если тип - строка, возвращаем как есть
        if param_type == str:
            return argument
        
        # Получить конвертер
        converter_class = CONVERTERS.get(param_type)
        if converter_class:
            converter = converter_class()
            return await converter.convert(ctx, argument)
        
        # Если тип - Union, попробуем первый тип
        if hasattr(param_type, '__origin__') and param_type.__origin__ is Union:
            for arg_type in param_type.__args__:
                converter_class = CONVERTERS.get(arg_type)
                if converter_class:
                    try:
                        converter = converter_class()
                        return await converter.convert(ctx, argument)
                    except:
                        continue
        
        # Если конвертер не найден, возвращаем как есть
        return argument
    
    async def _convert_args(self, ctx: Context, args: List[str], param: inspect.Parameter) -> List[Any]:
        """Конвертировать список аргументов для *args"""
        param_type = param.annotation
        
        if param_type == inspect.Parameter.empty or param_type == str:
            return args
        
        # Попытка конвертировать каждый аргумент
        converted = []
        for arg in args:
            try:
                conv = await self._convert_argument(ctx, arg, param)
                converted.append(conv)
            except:
                converted.append(arg)
        
        return converted


class CommandGroup:
    """Группа команд (для подкоманд)"""
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.commands: Dict[str, Command] = {}
        self.aliases: Dict[str, str] = {}
        self.description = kwargs.get('description', '')
        self.help = kwargs.get('help', self.description)
    
    def command(self, name: Optional[str] = None, **kwargs):
        """Декоратор для добавления подкоманды"""
        def decorator(func: Callable):
            cmd = Command(func, name=name, **kwargs)
            self.add_command(cmd)
            return cmd
        return decorator
    
    def add_command(self, command: Command):
        """Добавить команду в группу"""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.aliases[alias] = command.name
    
    def get_command(self, name: str) -> Optional[Command]:
        """Получить команду по имени"""
        return self.commands.get(name) or self.commands.get(self.aliases.get(name))


class Bot:
    """Расширенный клиент с поддержкой команд"""
    
    def __init__(self, client, command_prefix: Union[str, List[str], Callable] = "!", **options):
        self.client = client
        self.command_prefix = command_prefix
        self.commands: Dict[str, Command] = {}
        self.aliases: Dict[str, str] = {}
        self.groups: Dict[str, CommandGroup] = {}
        self.help_command = options.get('help_command', None)
        self.case_insensitive = options.get('case_insensitive', False)
        self.cog_manager = None  # Будет инициализирован при импорте cogs
        
        # Регистрация обработчика сообщений
        async def on_message_handler(message: Message):
            print(f"🔵🔵🔵 Bot.on_message_handler CALLED! Content: {message.content[:50] if message.content else 'None'}")
            print(f"🔵🔵🔵 Bot.on_message_handler: message.author.id={message.author.id if message.author else 'None'}")
            try:
                await self.process_commands(message)
                print(f"🔵🔵🔵 Bot.on_message_handler: process_commands completed")
            except Exception as e:
                print(f"❌❌❌ Error in Bot.on_message_handler: {e}")
                import traceback
                traceback.print_exc()
        
        # Зарегистрировать обработчик
        client.event("message")(on_message_handler)
        print(f"🔵 Bot: Registered message handler '{on_message_handler.__name__}', total handlers: {len(client.event_handlers.get('message', []))}")
        print(f"🔵 Bot: Handler function: {on_message_handler}")
        print(f"🔵 Bot: Registered handlers: {[h.__name__ if hasattr(h, '__name__') else str(h) for h in client.event_handlers.get('message', [])]}")
    
    def command(self, name: Optional[str] = None, **kwargs):
        """Декоратор для создания команды"""
        def decorator(func: Callable):
            cmd = Command(func, name=name, **kwargs)
            self.add_command(cmd)
            return cmd
        return decorator
    
    def group(self, name: Optional[str] = None, **kwargs):
        """Декоратор для создания группы команд"""
        def decorator(func: Callable):
            group_name = name or func.__name__
            group = CommandGroup(group_name, **kwargs)
            self.groups[group_name] = group
            
            # Создать команду-обертку
            @self.command(name=group_name, **kwargs)
            async def group_command(ctx: Context, *args, **kwargs):
                if args:
                    subcommand_name = args[0]
                    subcommand = group.get_command(subcommand_name)
                    if subcommand:
                        await subcommand.invoke(ctx, *args[1:], **kwargs)
                    else:
                        await ctx.send(f"Subcommand '{subcommand_name}' not found")
                else:
                    await ctx.send(f"Use `{ctx.prefix}{group_name} <subcommand>`")
            
            return group
        return decorator
    
    def add_command(self, command: Command):
        """Добавить команду"""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.aliases[alias] = command.name
    
    def get_command(self, name: str) -> Optional[Command]:
        """Получить команду по имени"""
        if self.case_insensitive:
            name = name.lower()
            for cmd_name, cmd in self.commands.items():
                if cmd_name.lower() == name:
                    return cmd
            alias = self.aliases.get(name)
            if alias:
                return self.commands.get(alias)
        else:
            return self.commands.get(name) or self.commands.get(self.aliases.get(name))
    
    def _get_prefix(self, message: Message) -> Optional[str]:
        """Получить префикс для сообщения"""
        if callable(self.command_prefix):
            return self.command_prefix(self.client, message)
        elif isinstance(self.command_prefix, list):
            content = message.content
            for prefix in self.command_prefix:
                if content.startswith(prefix):
                    return prefix
            return None
        else:
            if message.content.startswith(self.command_prefix):
                return self.command_prefix
            return None
    
    async def process_commands(self, message: Message):
        """Обработать команду из сообщения"""
        print(f"🔵 process_commands called: content={message.content[:50] if message.content else 'None'}, author={message.author.id if message.author else 'None'}")
        if not message.content:
            print("❌ No content, returning")
            return
        
        # Для selfbot не пропускать сообщения от самого бота (они могут быть командами)
        # if message.author.bot:
        #     return
        
        prefix = self._get_prefix(message)
        print(f"🔵 Prefix check: prefix={prefix}, content starts with prefix={message.content.startswith(prefix) if prefix else False}")
        if not prefix:
            print("❌ No prefix found, returning")
            return
        
        # Удалить префикс
        content = message.content[len(prefix):].strip()
        if not content:
            return
        
        # Разделить на команду и аргументы
        parts = content.split()
        command_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if self.case_insensitive:
            command_name = command_name.lower()
        
        print(f"🔵 Looking for command: '{command_name}'")
        print(f"🔵 Available commands: {list(self.commands.keys())}")
        print(f"🔵 Available aliases: {list(self.aliases.keys())}")
        
        # Найти команду
        command = self.get_command(command_name)
        print(f"🔵 Command found: {command.name if command else 'None'}")
        if not command:
            # Попытка найти группу
            group = self.groups.get(command_name)
            if group and args:
                subcommand_name = args[0]
                if self.case_insensitive:
                    subcommand_name = subcommand_name.lower()
                command = group.get_command(subcommand_name)
                if command:
                    args = args[1:]
                else:
                    return
            else:
                return
        
        if not command.enabled:
            return
        
        # Создать контекст
        try:
            print(f"🔵 Preparing command '{command.name}' with args: {args}")
            converted_args, converted_kwargs = await command.prepare(Context(message, command, prefix, args, {}, bot=self), args)
            print(f"🔵 Prepared args: {converted_args}, kwargs: {converted_kwargs}")
            ctx = Context(message, command, prefix, args, converted_kwargs, bot=self)
            print(f"🔵 Invoking command '{command.name}'...")
            result = await command.invoke(ctx, *converted_args, **converted_kwargs)
            print(f"🔵 Command '{command.name}' invoked, result: {result}")
        except CommandError as e:
            print(f"❌ CommandError in '{command.name}': {e}")
            await message.channel.send(f"❌ {e}") if message.channel else None
        except Exception as e:
            print(f"❌ Exception in '{command.name}': {e}")
            import traceback
            traceback.print_exc()
            # Обработка ошибок команд
            if hasattr(self.client, 'dispatch'):
                self.client.dispatch('command_error', message, command, e)
            else:
                import traceback
                traceback.print_exc()

