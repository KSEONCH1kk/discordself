"""Исключения для библиотеки Discord Selfbot"""

from typing import Optional, Any


class DiscordException(Exception):
    """Базовое исключение для всех ошибок Discord"""
    pass


class HTTPException(DiscordException):
    """Исключение при HTTP запросах"""
    def __init__(self, response: Optional[Any] = None, message: Optional[str] = None, status: Optional[int] = None):
        self.response = response
        if response:
            try:
                self.status = response.status if hasattr(response, 'status') else (response.status_code if hasattr(response, 'status_code') else status)
            except:
                self.status = status
        else:
            self.status = status
        self.message = message or f"HTTP {self.status}: {response.text if response and hasattr(response, 'text') else 'Unknown error'}"
        super().__init__(self.message)


class Forbidden(HTTPException):
    """403 Forbidden - недостаточно прав"""
    def __init__(self, response: Optional[Any] = None, message: Optional[str] = None):
        super().__init__(response, message or "Forbidden: You don't have permission to perform this action", 403)


class NotFound(HTTPException):
    """404 Not Found - ресурс не найден"""
    def __init__(self, response: Optional[Any] = None, message: Optional[str] = None):
        super().__init__(response, message or "Not Found: The requested resource was not found", 404)


class BadRequest(HTTPException):
    """400 Bad Request - неверный запрос"""
    def __init__(self, response: Optional[Any] = None, message: Optional[str] = None):
        super().__init__(response, message or "Bad Request: The request was invalid", 400)


class Unauthorized(HTTPException):
    """401 Unauthorized - не авторизован"""
    def __init__(self, response: Optional[Any] = None, message: Optional[str] = None):
        super().__init__(response, message or "Unauthorized: Invalid token or authentication failed", 401)


class RateLimitException(DiscordException):
    """Исключение при превышении rate limit"""
    def __init__(self, retry_after: float, message: Optional[str] = None):
        self.retry_after = retry_after
        self.message = message or f"Rate limit exceeded. Retry after {retry_after} seconds"
        super().__init__(self.message)


class WebSocketException(DiscordException):
    """Исключение при работе с WebSocket"""
    def __init__(self, code: int, message: Optional[str] = None):
        self.code = code
        self.message = message or f"WebSocket error {code}"
        super().__init__(self.message)


class LoginFailure(DiscordException):
    """Ошибка при входе в аккаунт"""
    pass


class ShardException(DiscordException):
    """Ошибка при работе с шардами"""
    pass


class CommandError(DiscordException):
    """Базовое исключение для ошибок команд"""
    pass


class CommandNotFound(CommandError):
    """Команда не найдена"""
    def __init__(self, command_name: str):
        self.command_name = command_name
        super().__init__(f"Command '{command_name}' not found")


class MissingRequiredArgument(CommandError):
    """Отсутствует обязательный аргумент"""
    def __init__(self, param_name: str):
        self.param_name = param_name
        super().__init__(f"Missing required argument: {param_name}")


class BadArgument(CommandError):
    """Неверный аргумент команды"""
    def __init__(self, message: Optional[str] = None):
        super().__init__(message or "Invalid argument provided")


class CheckFailure(CommandError):
    """Проверка команды не пройдена"""
    def __init__(self, message: Optional[str] = None):
        super().__init__(message or "Command check failed")


class MissingPermissions(CheckFailure):
    """Отсутствуют необходимые права"""
    def __init__(self, missing_permissions: list):
        self.missing_permissions = missing_permissions
        perms_str = ", ".join(missing_permissions)
        super().__init__(f"Missing required permissions: {perms_str}")


class BotMissingPermissions(CheckFailure):
    """У бота отсутствуют необходимые права"""
    def __init__(self, missing_permissions: list):
        self.missing_permissions = missing_permissions
        perms_str = ", ".join(missing_permissions)
        super().__init__(f"Bot is missing required permissions: {perms_str}")


class NoPrivateMessage(CheckFailure):
    """Команда не может быть выполнена в личных сообщениях"""
    def __init__(self):
        super().__init__("This command cannot be used in private messages")


class PrivateMessageOnly(CheckFailure):
    """Команда может быть выполнена только в личных сообщениях"""
    def __init__(self):
        super().__init__("This command can only be used in private messages")


class CommandOnCooldown(CommandError):
    """Команда на cooldown"""
    def __init__(self, command, retry_after: float):
        self.command = command
        self.retry_after = retry_after
        super().__init__(f"Command '{command.name}' is on cooldown. Try again in {retry_after:.2f} seconds")

