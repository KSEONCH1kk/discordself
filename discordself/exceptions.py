"""Исключения для библиотеки Discord Selfbot.

Этот модуль содержит все исключения, используемые в библиотеке
для обработки различных типов ошибок.
"""

from typing import Optional, Any


class DiscordException(Exception):
    """Базовое исключение для всех ошибок Discord.
    
    Все исключения библиотеки наследуются от этого класса.
    Используйте для общего перехвата всех ошибок DiscordSelf.
    """
    pass


class HTTPException(DiscordException):
    """Исключение при HTTP запросах к Discord API.
    
    Вызывается при ошибках HTTP запросов (4xx, 5xx).
    
    Attributes:
        response: Объект ответа HTTP
        status: HTTP статус код
        message: Сообщение об ошибке
    
    Args:
        response: Объект ответа HTTP (опционально)
        message: Сообщение об ошибке (опционально)
        status: HTTP статус код (опционально)
    """
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
    """403 Forbidden - недостаточно прав.
    
    Вызывается когда у пользователя/бота нет прав для выполнения действия.
    """
    def __init__(self, response: Optional[Any] = None, message: Optional[str] = None):
        super().__init__(response, message or "Forbidden: You don't have permission to perform this action", 403)


class NotFound(HTTPException):
    """404 Not Found - ресурс не найден.
    
    Вызывается когда запрашиваемый ресурс (канал, сообщение и т.д.) не существует.
    """
    def __init__(self, response: Optional[Any] = None, message: Optional[str] = None):
        super().__init__(response, message or "Not Found: The requested resource was not found", 404)


class BadRequest(HTTPException):
    """400 Bad Request - неверный запрос.
    
    Вызывается когда запрос к Discord API некорректен (неверные параметры и т.д.).
    """
    def __init__(self, response: Optional[Any] = None, message: Optional[str] = None):
        super().__init__(response, message or "Bad Request: The request was invalid", 400)


class Unauthorized(HTTPException):
    """401 Unauthorized - не авторизован.
    
    Вызывается когда токен невалиден или истек срок действия.
    """
    def __init__(self, response: Optional[Any] = None, message: Optional[str] = None):
        super().__init__(response, message or "Unauthorized: Invalid token or authentication failed", 401)


class RateLimitException(DiscordException):
    """Исключение при превышении rate limit.
    
    Вызывается когда превышен лимит запросов к Discord API.
    
    Attributes:
        retry_after: Время в секундах до следующего запроса
    
    Args:
        retry_after: Время в секундах до следующего запроса
        message: Сообщение об ошибке (опционально)
    """
    def __init__(self, retry_after: float, message: Optional[str] = None):
        self.retry_after = retry_after
        self.message = message or f"Rate limit exceeded. Retry after {retry_after} seconds"
        super().__init__(self.message)


class WebSocketException(DiscordException):
    """Исключение при работе с WebSocket.
    
    Вызывается при ошибках WebSocket соединения с Discord Gateway.
    
    Attributes:
        code: Код ошибки WebSocket
    
    Args:
        code: Код ошибки WebSocket
        message: Сообщение об ошибке (опционально)
    """
    def __init__(self, code: int, message: Optional[str] = None):
        self.code = code
        self.message = message or f"WebSocket error {code}"
        super().__init__(self.message)


class LoginFailure(DiscordException):
    """Ошибка при входе в аккаунт.
    
    Вызывается когда не удалось войти в Discord аккаунт
    (неверный токен, проблемы с подключением и т.д.).
    """
    pass


class ShardException(DiscordException):
    """Ошибка при работе с шардами.
    
    Вызывается при ошибках шардирования (неверное количество шардов и т.д.).
    """
    pass


class CommandError(DiscordException):
    """Базовое исключение для ошибок команд.
    
    Все исключения, связанные с системой команд, наследуются от этого класса.
    """
    pass


class CommandNotFound(CommandError):
    """Команда не найдена.
    
    Вызывается когда пользователь пытается выполнить несуществующую команду.
    
    Attributes:
        command_name: Имя команды, которая не была найдена
    
    Args:
        command_name: Имя команды
    """
    def __init__(self, command_name: str):
        self.command_name = command_name
        super().__init__(f"Command '{command_name}' not found")


class MissingRequiredArgument(CommandError):
    """Отсутствует обязательный аргумент.
    
    Вызывается когда команда вызвана без обязательного аргумента.
    
    Attributes:
        param_name: Имя отсутствующего параметра
    
    Args:
        param_name: Имя параметра
    """
    def __init__(self, param_name: str):
        self.param_name = param_name
        super().__init__(f"Missing required argument: {param_name}")


class BadArgument(CommandError):
    """Неверный аргумент команды.
    
    Вызывается когда аргумент команды не может быть преобразован
    в требуемый тип или не проходит валидацию.
    
    Args:
        message: Сообщение об ошибке (опционально)
    """
    def __init__(self, message: Optional[str] = None):
        super().__init__(message or "Invalid argument provided")


class CheckFailure(CommandError):
    """Проверка команды не пройдена.
    
    Вызывается когда команда не прошла проверку (checks).
    Базовый класс для MissingPermissions, NoPrivateMessage и т.д.
    
    Args:
        message: Сообщение об ошибке (опционально)
    """
    def __init__(self, message: Optional[str] = None):
        super().__init__(message or "Command check failed")


class MissingPermissions(CheckFailure):
    """Отсутствуют необходимые права.
    
    Вызывается когда у пользователя нет необходимых прав для выполнения команды.
    
    Attributes:
        missing_permissions: Список отсутствующих прав
    
    Args:
        missing_permissions: Список названий отсутствующих прав
    """
    def __init__(self, missing_permissions: list):
        self.missing_permissions = missing_permissions
        perms_str = ", ".join(missing_permissions)
        super().__init__(f"Missing required permissions: {perms_str}")


class BotMissingPermissions(CheckFailure):
    """У бота отсутствуют необходимые права.
    
    Вызывается когда у бота нет необходимых прав для выполнения команды.
    
    Attributes:
        missing_permissions: Список отсутствующих прав
    
    Args:
        missing_permissions: Список названий отсутствующих прав
    """
    def __init__(self, missing_permissions: list):
        self.missing_permissions = missing_permissions
        perms_str = ", ".join(missing_permissions)
        super().__init__(f"Bot is missing required permissions: {perms_str}")


class NoPrivateMessage(CheckFailure):
    """Команда не может быть выполнена в личных сообщениях.
    
    Вызывается когда команда, предназначенная только для гильдий,
    вызывается в личных сообщениях.
    """
    def __init__(self):
        super().__init__("This command cannot be used in private messages")


class PrivateMessageOnly(CheckFailure):
    """Команда может быть выполнена только в личных сообщениях.
    
    Вызывается когда команда, предназначенная только для личных сообщений,
    вызывается в гильдии.
    """
    def __init__(self):
        super().__init__("This command can only be used in private messages")


class CommandOnCooldown(CommandError):
    """Команда на cooldown.
    
    Вызывается когда команда вызывается слишком часто и находится на cooldown.
    
    Attributes:
        command: Объект команды
        retry_after: Время в секундах до следующего использования
    
    Args:
        command: Объект команды
        retry_after: Время в секундах до следующего использования
    """
    def __init__(self, command, retry_after: float):
        self.command = command
        self.retry_after = retry_after
        super().__init__(f"Command '{command.name}' is on cooldown. Try again in {retry_after:.2f} seconds")

