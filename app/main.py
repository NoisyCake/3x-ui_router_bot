import os
import dotenv
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from handlers import admin, user
from keyboards.main_menu import set_main_menu
from lexicon.lexicon import LEXICON
from database.engine import create_db, async_session
from middlewares.db import DataBaseSession
from middlewares.http_client import XUIMiddleware


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
    
    # Инициализация хранилища Redis
    redis = Redis(host='localhost')
    storage = RedisStorage(redis=redis)
    
    # Инициализация бота с диспетчером
    bot = Bot(
        token=os.getenv('BOT_TOKEN'),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)
    
    # Регистрация роутеров
    dp.include_router(admin.router)
    dp.include_router(user.router)
    
    # Регистрация мидлварей
    dp.update.middleware(DataBaseSession(session_pool=async_session))
    dp.update.middleware(XUIMiddleware(
        base_url=os.getenv('XUI_URL'),
        username=os.getenv('XUI_USERNAME'),
        password=os.getenv('XUI_PASSWORD')
    ))

    # Установка описания и меню бота
    await bot.set_my_description(LEXICON['description'])
    await set_main_menu(bot)
    
    # Пропуск апдейтов, пришедших в неактивный период бота
    await bot.delete_webhook(drop_pending_updates=True)
    # Запуск поллинга
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")