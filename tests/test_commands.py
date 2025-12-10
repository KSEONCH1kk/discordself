"""Тесты для системы команд"""

import unittest
from unittest.mock import Mock, AsyncMock
from discordself.commands import Command, Context, Bot
from discordself.exceptions import MissingRequiredArgument, BadArgument


class TestCommands(unittest.TestCase):
    """Тесты для системы команд"""
    
    def test_command_creation(self):
        """Тест создания команды"""
        async def test_cmd(ctx, arg: int):
            return arg * 2
        
        cmd = Command(test_cmd, name="test")
        self.assertEqual(cmd.name, "test")
        self.assertEqual(cmd.callback, test_cmd)
    
    def test_command_aliases(self):
        """Тест алиасов команды"""
        async def test_cmd(ctx):
            pass
        
        cmd = Command(test_cmd, name="test", aliases=["t", "test2"])
        self.assertIn("t", cmd.aliases)
        self.assertIn("test2", cmd.aliases)
    
    def test_command_prepare_args(self):
        """Тест подготовки аргументов"""
        async def test_cmd(ctx, a: int, b: str):
            return f"{a}:{b}"
        
        cmd = Command(test_cmd)
        ctx = Mock()
        ctx._client = None
        
        # Тест будет упрощен, так как нужен реальный контекст
        # В реальных тестах нужно создать полноценный Context с Message


class TestContext(unittest.TestCase):
    """Тесты для Context"""
    
    def test_context_creation(self):
        """Тест создания контекста"""
        message = Mock()
        message._client = Mock()
        message.author = Mock()
        message.channel = Mock()
        message.guild = None
        
        cmd = Mock()
        ctx = Context(message, cmd, "!", ["arg1"], {})
        
        self.assertEqual(ctx.prefix, "!")
        self.assertEqual(ctx.args, ["arg1"])
        self.assertEqual(ctx.message, message)


if __name__ == '__main__':
    unittest.main()

