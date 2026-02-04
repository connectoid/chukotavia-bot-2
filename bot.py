import os
import dotenv
import logging
import asyncio
import random
from time import sleep
from datetime import datetime
from pprint import pprint

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import apscheduler.schedulers.background

from config_data.config import load_config
from handlers import other_handlers, user_handlers
from service.tools import request_tickets
from database.orm import get_all_users, get_tickets, get_ticket_by_id
from keyboards.commands_menu import set_commands_menu
from service.tools import save_db_to_json, load_dict_from_json

dotenv.load_dotenv()
config = load_config('.env')

BOT_TOKEN = config.tg_bot.token
LOG_FILE = 'chukotabia-bot-2.log'
REQUEST_INTERVAL = 60
EVERYDAY_MESSAGE_HOUR = 1
EVERYDAY_MESSAGE_MINUTE = 0
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')


scheduler = AsyncIOScheduler()
# scheduler = apscheduler.schedulers.background.BackgroundScheduler({'apscheduler.job_defaults.max_instances': 5})

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main():
    # dotenv.load_dotenv()
    # config = load_config('.env')
    # BOT_TOKEN = config.tg_bot.token
    # LOG_FILE = 'chukotabia-bot-2.log'
    logging.basicConfig(level=logging.WARNING,
                        filename=LOG_FILE,
                        filemode='a',
                        format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
                        '%(lineno)d - %(name)s - %(message)s')
    # bot = Bot(token=BOT_TOKEN)
    # dp = Dispatcher()
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)
    await schedule_jobs()
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def send_message_to_users(dp: Dispatcher):
    users = get_all_users()
    for user in users:
        if user.everyday_message:
            print(f'Sending everyday message to user {user.tg_id}')
            await bot.send_message(chat_id=user.tg_id, text='Все нормально, я работаю') 
            await asyncio.sleep(2)


async def send_message_to_user(user_tg_id, message_text):
        await bot.send_message(chat_id=user_tg_id, text=message_text) 


async def request_dates(dp: Dispatcher):
    print('REQUESTING DATES')
    interval = random.randint(55, 165)
    interval = 1
    all_users = load_dict_from_json()
    for user in all_users:
        user_tg_id = user['tg_id']
        user_tg_username = user['username']
        print(f'Requesting for user {user_tg_id} {user_tg_username}')
        user_tickets = user['tickets']
        for user_ticket in user_tickets:
            result, ticket_message = request_tickets(user_ticket['date'], user_ticket['direction'])
            if result:
                await bot.send_message(chat_id=user['tg_id'], text=ticket_message) 
            await asyncio.sleep(interval)
        await asyncio.sleep(interval)
        # sleep(interval)
        

async def schedule_jobs():
    scheduler.add_job(
        send_message_to_users, 'cron', day_of_week='*',
        hour=EVERYDAY_MESSAGE_HOUR, minute=EVERYDAY_MESSAGE_MINUTE, end_date='2030-12-31' , args=(dp,))
    scheduler.add_job(request_dates, 'interval', seconds = REQUEST_INTERVAL, args=(dp,), max_instances=2)


if __name__ == '__main__':
    dp.startup.register(set_commands_menu)
    # all_users = get_all_users_from_db()
    save_db_to_json()
    logging.info('Бот запущен')
    asyncio.run(main())
    
