import os
import dotenv
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config_data.config import load_config
from handlers import other_handlers, user_handlers
from service.tools import check_and_convert_date

async def main():
    dotenv.load_dotenv()
    config = load_config('.env')
    BOT_TOKEN = config.tg_bot.token
    LOG_FILE = 'chukotabia-bot-2.log'
    logging.basicConfig(level=logging.INFO,
                        filename=LOG_FILE,
                        filemode='a',
                        format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
                        '%(lineno)d - %(name)s - %(message)s')
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.info('Бот запущен')
    asyncio.run(main())