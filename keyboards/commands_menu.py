from aiogram import Bot
from aiogram.types import BotCommand

# Функция для настройки кнопки Menu бота
async def set_commands_menu(bot: Bot):
    await bot.delete_my_commands()
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запуск бота'),
        BotCommand(command='/help',
                   description='Мправка по работе бота'),
        BotCommand(command='/give_premium',
                   description='Дать пользователям доступ ко всем функциям бота (только для администраторов)')
    ]
    await bot.set_my_commands(main_menu_commands)