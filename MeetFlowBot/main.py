import asyncio  # асинхронная библиотека
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher  
from aiogram.fsm.storage.memory import MemoryStorage  # хранилища данных для состояний пользователей
from config_beforeOS import API_TOKEN
from logging_config import setup_logging, logger
from handlers import router as user_router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode  # настройки разметки сообщений (HTML, Markdown)
load_dotenv()


async def main():
    setup_logging()
    logger.info("Start bot")
    # bot = Bot(token=os.getenv('API_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()  # Хранилище для состояний
    dp = Dispatcher(storage=storage)  # объект диспетчера, все данные бота, что не будут сохранены в базу
    # данных, будут стерты при перезапуске
    dp.include_router(user_router)  # подключает к нашему диспетчеру все обработчики, которые используют router
    await bot.delete_webhook(drop_pending_updates=True)  # бот удаляет все обновления, которые произошли после
    # последнего завершения работы бота

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())  # старт работы бота
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":  # защита от ложного срабатывания кода
    asyncio.run(main())  # запуск асинхронный main
