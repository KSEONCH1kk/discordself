"""Help Command Generator для команд"""

import inspect
from typing import Optional, Dict, List
from .commands import Bot, Command, CommandGroup, Context
from .embeds import Embed


class HelpCommand:
    """Базовый класс для help команд"""
    
    def __init__(self, **options):
        self.command_attrs = options.get('command_attrs', {})
        self.verify_checks = options.get('verify_checks', True)
        self.show_hidden = options.get('show_hidden', False)
        self.sort_commands = options.get('sort_commands', True)
        self.width = options.get('width', 80)
        self.indent = options.get('indent', 2)
    
    async def send_bot_help(self, ctx: Context, mapping: Dict):
        """Отправить справку по всем командам"""
        raise NotImplementedError("Must implement send_bot_help")
    
    async def send_command_help(self, ctx: Context, command: Command):
        """Отправить справку по команде"""
        raise NotImplementedError("Must implement send_command_help")
    
    async def send_group_help(self, ctx: Context, group: CommandGroup):
        """Отправить справку по группе команд"""
        raise NotImplementedError("Must implement send_group_help")
    
    async def command_not_found(self, ctx: Context, command: str):
        """Обработка не найденной команды"""
        return f"Команда '{command}' не найдена."
    
    async def subcommand_not_found(self, ctx: Context, command: Command, subcommand: str):
        """Обработка не найденной подкоманды"""
        return f"Подкоманда '{subcommand}' команды '{command.name}' не найдена."


class DefaultHelpCommand(HelpCommand):
    """Стандартная реализация help команды"""
    
    def __init__(self, **options):
        super().__init__(**options)
        self.paginator = None
    
    def get_bot_mapping(self, ctx: Context) -> Dict:
        """Получить маппинг команд бота"""
        bot = ctx.bot
        # Если bot - это Client, нужно получить Bot из него
        if bot and not hasattr(bot, 'commands'):
            # Попробовать найти Bot через message
            if hasattr(ctx.message, '_client') and hasattr(ctx.message._client, 'commands'):
                bot = ctx.message._client
            else:
                # Если не нашли, вернуть пустой маппинг
                return {}
        
        if not bot or not hasattr(bot, 'commands'):
            return {}
        
        mapping = {}
        
        # Группировать команды по категориям (cogs)
        for command in bot.commands.values():
            if command.hidden and not self.show_hidden:
                continue
            
            # Получить категорию (cog name или "Other")
            cog_name = getattr(command, 'cog_name', None) or "Other"
            if cog_name not in mapping:
                mapping[cog_name] = []
            mapping[cog_name].append(command)
        
        return mapping
    
    async def send_bot_help(self, ctx: Context, mapping: Optional[Dict] = None):
        """Отправить справку по всем командам"""
        if mapping is None:
            mapping = self.get_bot_mapping(ctx)
        
        embed = Embed(title="📚 Справка по командам", color=0x5865F2)
        
        # Добавить описание бота если есть
        if ctx.bot and hasattr(ctx.bot, 'description'):
            embed.description = ctx.bot.description or "Используйте `!help <команда>` для получения подробной информации."
        else:
            embed.description = "Используйте `!help <команда>` для получения подробной информации."
        
        # Добавить команды по категориям
        for cog_name, commands in mapping.items():
            if not commands:
                continue
            
            # Отсортировать команды
            if self.sort_commands:
                commands = sorted(commands, key=lambda c: c.name)
            
            # Создать список команд
            command_list = []
            for command in commands:
                if command.hidden and not self.show_hidden:
                    continue
                
                # Проверить доступность команды
                if self.verify_checks:
                    try:
                        can_run = await command.can_run(ctx)
                        if not can_run:
                            continue
                    except:
                        continue
                
                command_list.append(f"`{command.name}` - {command.description}")
            
            if command_list:
                embed.add_field(
                    name=cog_name,
                    value="\n".join(command_list[:10]),  # Ограничить до 10 команд
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    async def send_command_help(self, ctx: Context, command: Command):
        """Отправить справку по команде"""
        embed = Embed(title=f"Команда: {command.name}", color=0x5865F2)
        
        # Описание
        embed.description = command.help or command.description or "Нет описания"
        
        # Использование
        usage = f"`{ctx.prefix}{command.name}"
        if command.params:
            for param in command.params:
                if param.default == inspect.Parameter.empty:
                    usage += f" <{param.name}>"
                else:
                    usage += f" [{param.name}]"
        usage += "`"
        embed.add_field(name="Использование", value=usage, inline=False)
        
        # Алиасы
        if command.aliases:
            embed.add_field(name="Алиасы", value=", ".join(f"`{alias}`" for alias in command.aliases), inline=False)
        
        await ctx.send(embed=embed)
    
    async def send_group_help(self, ctx: Context, group: CommandGroup):
        """Отправить справку по группе команд"""
        embed = Embed(title=f"Группа команд: {group.name}", color=0x5865F2)
        
        embed.description = group.description or "Нет описания"
        
        # Подкоманды
        if group.commands:
            subcommands = []
            for cmd in group.commands.values():
                if cmd.hidden and not self.show_hidden:
                    continue
                subcommands.append(f"`{cmd.name}` - {cmd.description}")
            
            if subcommands:
                embed.add_field(name="Подкоманды", value="\n".join(subcommands), inline=False)
        
        await ctx.send(embed=embed)


def setup_help_command(bot: Bot, help_command: Optional[HelpCommand] = None):
    """Настроить help команду для бота"""
    if help_command is None:
        help_command = DefaultHelpCommand()
    
    bot.help_command = help_command
    
    # Создать help команду
    @bot.command(name="help", description="Показать справку по командам")
    async def help_impl(ctx: Context, command: Optional[str] = None):
        """Показать справку по командам"""
        if command is None:
            # Показать все команды
            await help_command.send_bot_help(ctx)
        else:
            # Найти команду
            cmd = bot.get_command(command)
            if cmd:
                if isinstance(cmd, CommandGroup):
                    await help_command.send_group_help(ctx, cmd)
                else:
                    await help_command.send_command_help(ctx, cmd)
            else:
                message = await help_command.command_not_found(ctx, command)
                await ctx.send(message)

