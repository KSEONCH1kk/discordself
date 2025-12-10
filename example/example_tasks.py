"""Пример использования Tasks (периодические задачи)"""

from discordself import Client, Intents
from discordself.commands import Bot
from discordself.tasks import loop

client = Client(
    token="YOUR_TOKEN_HERE",
    intents=Intents.GUILDS
)

bot = Bot(client, command_prefix="!")


@loop(seconds=60)  # Каждую минуту
async def status_update():
    """Обновление статуса каждую минуту"""
    import random
    statuses = ["Играет", "Слушает", "Смотрит"]
    status = random.choice(statuses)
    print(f"Обновление статуса: {status}")


@loop(minutes=5)  # Каждые 5 минут
async def check_updates():
    """Проверка обновлений каждые 5 минут"""
    print("Проверка обновлений...")


@loop(hours=1, count=24)  # Каждый час, всего 24 раза
async def hourly_task():
    """Задача, выполняемая каждый час, всего 24 раза"""
    print("Выполнение ежечасной задачи...")


@status_update.before_loop
async def before_status_update():
    """Выполняется перед запуском задачи обновления статуса"""
    print("Ожидание готовности бота...")
    await bot.client.wait_until_ready()
    print("Бот готов, запуск задачи обновления статуса")


@status_update.after_loop
async def after_status_update():
    """Выполняется после завершения задачи"""
    print("Задача обновления статуса завершена")


@status_update.error
async def status_update_error(error):
    """Обработка ошибок в задаче"""
    print(f"Ошибка в задаче обновления статуса: {error}")


@bot.command(name="start_tasks")
async def start_tasks(ctx):
    """Запустить все задачи"""
    status_update.start(bot)
    check_updates.start(bot)
    hourly_task.start(bot)
    await ctx.send("✅ Все задачи запущены!")


@bot.command(name="stop_tasks")
async def stop_tasks(ctx):
    """Остановить все задачи"""
    status_update.cancel()
    check_updates.cancel()
    hourly_task.cancel()
    await ctx.send("✅ Все задачи остановлены!")


@client.event("ready")
async def on_ready():
    print(f"✅ Бот готов: {client.user}")
    # Автоматически запустить задачу обновления статуса
    status_update.start(bot)


async def main():
    async with client:
        await asyncio.sleep(3600 * 24)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

