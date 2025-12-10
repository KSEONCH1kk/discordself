"""Tasks (периодические задачи) для Discord Selfbot"""

import asyncio
import logging
from typing import Callable, Optional, Any
from functools import wraps

logger = logging.getLogger(__name__)


class Loop:
    """Класс для периодических задач"""
    
    def __init__(self, coro: Callable, seconds: Optional[float] = None, minutes: Optional[float] = None, 
                 hours: Optional[float] = None, count: Optional[int] = None, reconnect: bool = True):
        self.coro = coro
        self.seconds = seconds or 0
        self.minutes = minutes or 0
        self.hours = hours or 0
        self.count = count
        self.reconnect = reconnect
        self._task: Optional[asyncio.Task] = None
        self._current_loop = 0
        self._before_loop: Optional[Callable] = None
        self._after_loop: Optional[Callable] = None
        self._error: Optional[Callable] = None
        self._is_being_cancelled = False
        self._injected = None
    
    @property
    def interval(self) -> float:
        """Интервал выполнения в секундах"""
        return self.seconds + (self.minutes * 60) + (self.hours * 3600)
    
    def before_loop(self, coro: Callable):
        """Декоратор для функции, выполняемой перед запуском цикла"""
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("before_loop must be a coroutine function")
        self._before_loop = coro
        return coro
    
    def after_loop(self, coro: Callable):
        """Декоратор для функции, выполняемой после завершения цикла"""
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("after_loop must be a coroutine function")
        self._after_loop = coro
        return coro
    
    def error(self, coro: Callable):
        """Декоратор для обработчика ошибок"""
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("error must be a coroutine function")
        self._error = coro
        return coro
    
    async def _call_loop_function(self, func: Callable, *args, **kwargs):
        """Вызвать функцию цикла"""
        if func is None:
            return
        
        try:
            if self._injected:
                return await func(self._injected, *args, **kwargs)
            return await func(*args, **kwargs)
        except Exception as e:
            if self._error:
                try:
                    await self._call_loop_function(self._error, e)
                except:
                    logger.error(f"Error in error handler for loop {self.coro.__name__}", exc_info=True)
            else:
                logger.error(f"Error in loop {self.coro.__name__}", exc_info=True)
    
    async def _loop(self):
        """Основной цикл задачи"""
        try:
            # Выполнить before_loop
            await self._call_loop_function(self._before_loop)
            
            # Основной цикл
            while True:
                # Проверить count
                if self.count is not None and self._current_loop >= self.count:
                    break
                
                # Выполнить задачу
                await self._call_loop_function(self.coro)
                
                self._current_loop += 1
                
                # Ожидание
                await asyncio.sleep(self.interval)
        
        except asyncio.CancelledError:
            self._is_being_cancelled = True
            raise
        except Exception as e:
            await self._call_loop_function(self._error, e)
        finally:
            # Выполнить after_loop
            await self._call_loop_function(self._after_loop)
    
    def start(self, *args, **kwargs):
        """Запустить задачу"""
        if self._task is not None and not self._task.done():
            raise RuntimeError("Loop is already running")
        
        if self.interval <= 0:
            raise ValueError("Loop interval must be greater than 0")
        
        self._injected = args[0] if args else None
        self._task = asyncio.create_task(self._loop())
        return self._task
    
    def cancel(self):
        """Отменить задачу"""
        if self._task is not None and not self._task.done():
            self._task.cancel()
    
    def restart(self, *args, **kwargs):
        """Перезапустить задачу"""
        self.cancel()
        self._current_loop = 0
        self.start(*args, **kwargs)
    
    def is_running(self) -> bool:
        """Проверить, запущена ли задача"""
        return self._task is not None and not self._task.done()


def loop(*, seconds: Optional[float] = None, minutes: Optional[float] = None, 
         hours: Optional[float] = None, count: Optional[int] = None, reconnect: bool = True):
    """Декоратор для создания периодической задачи"""
    def decorator(func: Callable) -> Loop:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Loop function must be a coroutine function")
        
        loop_obj = Loop(func, seconds=seconds, minutes=minutes, hours=hours, count=count, reconnect=reconnect)
        return loop_obj
    
    return decorator

