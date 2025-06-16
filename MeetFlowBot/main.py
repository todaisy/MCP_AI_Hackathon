import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher  # функции библиотеки для тг
from aiogram.fsm.storage.memory import MemoryStorage  # хранилища данных для состояний пользователей
from logging_config import setup_logging, logger
from handlers import router as user_router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
load_dotenv()


async def main():
    setup_logging()
    logger.info("Start bot")
    bot = Bot(token=os.getenv('API_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(user_router)  # подключает к нашему диспетчеру все обработчики, которые используют router
    await bot.delete_webhook(drop_pending_updates=True)  # бот удаляет все обновления, которые произошли после

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())  # старт работы бота
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":  # защита от ложного срабатывания кода
    asyncio.run(main())  # запуск асинхронный main
