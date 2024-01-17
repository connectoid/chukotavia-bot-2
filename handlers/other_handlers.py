from aiogram.types import Message
from aiogram import Router

router = Router()

@router.message()
async def send_echo(message: Message):
    try:
        # await message.send_copy(chat_id=message.chat.id)
        await message.reply(text='Данная команда не поддерживается. Список команд можно посмотреть в разделе /help')
    except TypeError:
        await message.reply(text='no_echo')