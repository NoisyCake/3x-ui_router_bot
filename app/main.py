import os
import dotenv
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers import admin, user
from keyboards.main_menu import set_main_menu
from lexicon.lexicon import LEXICON
from database.engine import create_db, async_session
from middlewares.db import DataBaseSession


# Загрузка переменных окружения
dotenv.load_dotenv()
# Инициализация логера
logger = logging.getLogger(__name__)


async def main():
    # Конфигурация логирования
    logging.basicConfig(
        level=logging.INFO,
        format='[{asctime}] #{levelname:8} {filename}:'
               '{lineno} - {name} - {message}',
        style='{'
    )
    
    # Подключение к базе данных
    await create_db()
    
    # Инициализация бота с диспетчером
    bot = Bot(
        token=os.getenv('BOT_TOKEN'),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(admin.router)
    dp.include_router(user.router)
    
    # Регистрация мидлварей
    dp.update.middleware(DataBaseSession(session_pool=async_session))

    # Установка описания и меню бота
    await bot.set_my_description(LEXICON['description'])
    await set_main_menu(bot)
    
    # Пропуск апдейтов, пришедших в неактивный период бота
    await bot.delete_webhook(drop_pending_updates=True)
    # Запуск поллинга
    await dp.start_polling(bot)
    
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")