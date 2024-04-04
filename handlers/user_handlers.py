from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram import Router, F 
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from keyboards.keyboards import (main_menu, direction_keyboard, yes_no_keyboard,
                                 create_del_request_keyboard, create_everyday_message_keyboard,
                                 create_give_premium_keyboard)
from database.orm import (add_user, add_ticket, get_tickets, delete_ticket,get_ticket_by_id,
                          get_date_and_direction_from_ticket_id, get_user_settings, disable_everyday_message,
                          enable_everyday_message, is_premium_user, get_all_users, enable_premium, 
                          disable_premium, get_user)
from service.tools import check_date, convert_date, request_tickets
from config_data.config import load_config

router = Router()
storage = MemoryStorage()

class FSMAddDate(StatesGroup):
    add_date = State()
    add_direction = State()

config = load_config('.env')
ADMINS = config.tg_bot.admins

date_dict = {}
directions = {
    'PVS_DYR': 'Провидения - Анадырь',
    'DYR_PVS': 'Анадырь - Провидения',
    'ЭГТ_DYR': 'Эгвекинот - Анадырь',
    'DYR_ЭГТ': 'Анадырь - Эгвекинот',
    'ЗЛА_DYR': 'Лаврентия - Анадырь',
    'DYR_ЗЛА': 'Анадырь - Лаврентия',
}

HELP_MESSAGE = ('Для работы с ботом используйте следующие режимы:\n\n'
                'Добавить билет - добавление даты вылета и выбор направления. После добавления билета, '
                'бот начинает мониторить появление в продаже билета на заданную дату. Запрос выполняется '
                'каждые 5 минут\n\n'
                'Посмотреть билеты - просмотр всех добавленных билетов. По каждому билету можно сразу '
                'выполнить проверку наличия в продаже нажав кнопку "Проверить" под билетом. Так же можно '
                'удалить любой билет кнопкой "Удалить"\n\n'
                'Настройки - здесь можно включить или выключить ежедневную отправку сообщения о работе бота. '
                'Она выполняется каждый день в 12-00, чтобы быть уверенным что бот работает\n\n'
                'ВНИМАНИЕ: Если бот не отвечает на запрос сразу, подождите некоторое время и не делайте '
                'повторные запросы. Если бот не отвечает дольше 2-3 минут, просьба сообщить на @connectoid\n\n'
                'По всем вопросам и предложениям можно обращаться к автору бота на @connectoid')

@router.message(CommandStart(), StateFilter(default_state))
async def proccess_start_command(message: Message):
    response = add_user(message.from_user.id, message.from_user.username)
    await message.answer('Приветствую. Вы запустили бот, который мониторит наличие в продаже билетов '
                         'авиакомпании Чукотавиа на заданные маршрут и дату. Краткую инструкцию по работе '
                         'с ботом можно посмотреть в разделе Помощь в главном меню или выполнив команду /help.',
                         reply_markup=main_menu)
    

@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text='ℹ️ Отменять нечего. Вы не в процессе добавления билета\n',
                         reply_markup=main_menu)
    

@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text='Вы вышли из процесса добавления билета\n\n',
                         reply_markup=main_menu)
    await state.clear()


@router.message(Command(commands='adddate'), StateFilter(default_state))
@router.message(F.text == 'Добавить билет', StateFilter(default_state))
async def process_adddate_command(message: Message, state: FSMContext):
    if is_premium_user(message.from_user.id):
        await message.answer(text='Пожалуйста, введите дату в формате ДД.ММ.ГГГГ\n'
                            'Если вы хотите прервать добавление билета - '
                                'отправьте команду /cancel',
                            show_alert=False)
        await state.set_state(FSMAddDate.add_date)
    else:
        await message.answer(text='ℹ️ У вас нет прав на использования бота!\n'
                            'Для получения доступа ко всем функциям бота, '
                            'напишите в Телеграм на @connectoid',
                            show_alert=False)


@router.callback_query(F.data == 'yes', StateFilter(default_state))
async def process_adddate_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='Пожалуйста, введите дату в формате ДД.ММ.ГГГГ\n'
                'Если вы хотите прервать добавление билета - '
                             'отправьте команду /cancel')
    await state.set_state(FSMAddDate.add_date)
    

# Этот хэндлер будет срабатывать, если введена корректная дата
# и переводить в состояние ожидания ввода направления
@router.message(StateFilter(FSMAddDate.add_date), ~F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенную дату в хранилище по ключу "date"
    if check_date(message.text):
        date = convert_date(message.text)
        await state.update_data(date=date)
        await message.answer(text='Спасибо!\nА теперь выберите направление',
                            reply_markup=direction_keyboard)
        # Устанавливаем состояние ожидания ввода направления
        await state.set_state(FSMAddDate.add_direction)
    else:
        await message.answer(text='ℹ️ Вы ввели дату в неправильном формате или несуществующую дату\n'
                             'Пожалйста, введите дату в формате ДД.ММ.ГГГГ\n'
                             'Если вы хотите прервать добавление билета - '
                             'отправьте команду /cancel')


# Этот хэндлер будет срабатывать, если во время ввода даты
# будет введено что-то некорректное
@router.message(StateFilter(FSMAddDate.add_date))
async def warning_not_date(message: Message):
    await message.answer(
        text='ℹ️ То, что вы отправили не похоже на дату\n'
             'Пожалуйста, введите дату в формате ДД.ММ.ГГГГ\n'
             'Если вы хотите прервать добавление даты - '
             'отправьте команду /cancel'
    )


@router.callback_query(F.data == 'PVS_DYR')
@router.callback_query(F.data == 'DYR_PVS')
@router.callback_query(F.data == 'ЭГТ_DYR')
@router.callback_query(F.data == 'DYR_ЭГТ')
@router.callback_query(F.data == 'ЗЛА_DYR')
@router.callback_query(F.data == 'DYR_ЗЛА')
async def process_direction_sent(callback: CallbackQuery, state: FSMContext):
    # Cохраняем введенное направление в хранилище по ключу "direction"
    await state.update_data(direction=callback.data)
    date_dict[callback.from_user.id] = await state.get_data()
    await state.clear()
    # Отправляем в чат сообщение о выходе из машины состояний
    direction_ru = directions[date_dict[callback.from_user.id]["direction"]]
    direction_en = date_dict[callback.from_user.id]["direction"]
    date = date_dict[callback.from_user.id]["date"]
    if add_ticket(callback.from_user.id, date, direction_en):
        await callback.message.edit_text(
            text='Спасибо! Ваши данные сохранены!\n'
                f'Добавлен мониторинг билетов на {date} по маршруту {direction_ru}\n'
                'Добавить еще один билет?',
                reply_markup=yes_no_keyboard, row_width = 2)
    else:
        await callback.message.edit_text(
            text=f'ℹ️ Билет на {date} по маршруту {direction_ru} '
                'уже был добавлен ранее. Добавить другой билет?',
                reply_markup=yes_no_keyboard, row_width = 2)


@router.message(StateFilter(FSMAddDate.add_direction))
async def warning_not_direction(message: Message):
    await message.answer(
        text='ℹ️ Пожалуйста, воспользуйтесь кнопками для выбора направления!\n'
             'Если вы хотите прервать добавление билета - '
             'отправьте команду /cancel',
             reply_markup=direction_keyboard
    )


@router.callback_query(F.data == 'no')
async def process_direction_exit(callback: CallbackQuery, state: FSMContext):
    # await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        text='Спасибо! Вы вышли из процесса добавления билета\n',
             reply_markup=main_menu)


@router.message(Command(commands='help'))
@router.message(F.text == 'Помощь', StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(text=HELP_MESSAGE, 
                         reply_markup=main_menu)


@router.message(Command(commands='settings'))
@router.message(F.text == 'Настройки', StateFilter(default_state))
async def process_help_command(message: Message):
    everyday_message_on = get_user_settings(message.from_user.id)
    keyboard = create_everyday_message_keyboard(everyday_message_on)
    await message.answer(text=f'Ежедневное сообщение о работе бота {"включено" if everyday_message_on else "выключено"}', 
                         reply_markup=keyboard)


@router.callback_query(F.data == 'everyday_message_on')
async def process_enable_everyday_message(callback: CallbackQuery):
    enable_everyday_message(callback.from_user.id)
    keyboard = create_everyday_message_keyboard(True)
    await callback.message.edit_text(text='Ежедневное сообщение о работе бота включено')
    await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(F.data == 'everyday_message_off')
async def process_disable_everyday_message(callback: CallbackQuery):
    disable_everyday_message(callback.from_user.id)
    keyboard = create_everyday_message_keyboard(False)
    await callback.message.edit_text(text='Ежедневное сообщение о работе бота выключено')
    await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.message(Command(commands='gettickets'))
@router.message(F.text == 'Посмотреть билеты')
async def process_gettickets_command(message: Message):
    tickets = get_tickets(message.from_user.id)
    if tickets:
        await message.answer(text=f'В мониторинге находятся следующие даты:', 
                                reply_markup=main_menu)
        for ticket in tickets:
            del_request_keyboard = create_del_request_keyboard(ticket.id)
            await message.answer(text=f'{ticket.date} - {directions[ticket.direction]}',
                                 reply_markup=del_request_keyboard,
                                 row_width = 2)
    else:
        await message.answer(text=f'ℹ️ У вас еще не добавлено ни однго билета', 
                                reply_markup=main_menu)
        
    
@router.callback_query(lambda x: 'delete_' in x.data)
async def process_delete_ticket(callback: CallbackQuery):
    # await callback.message.delete()
    ticket_id = callback.data.split('_')[1]
    date, direction = get_date_and_direction_from_ticket_id(ticket_id)
    delete_ticket(ticket_id)
    await callback.message.delete()
    await callback.message.answer(
        text=f'Билет на {date} по маршруту {directions[direction]} удален из мониторинга\n',
             reply_markup=main_menu)


@router.callback_query(lambda x: 'request_' in x.data)
async def process_request_ticket(callback: CallbackQuery):
    ticket_id = callback.data.split('_')[1]
    ticket = get_ticket_by_id(ticket_id)
    result, ticket_message = request_tickets(ticket.date, ticket.direction)
    await callback.message.answer(
        text=ticket_message,
             reply_markup=main_menu)


@router.message(Command(commands='give_premium'))
async def process_give_premium_command(message: Message):
    if str(message.from_user.id) in ADMINS:
        users = get_all_users()
        for user in users:
            premium_user = is_premium_user(user.tg_id)
            keyboard = create_give_premium_keyboard(premium_user, user.tg_id, user.username)
            await message.answer(text=f'{user.tg_id} ({user.username}): Премиум {"включен" if premium_user else "выключен"}', 
                            reply_markup=keyboard)
    else:
        await message.answer(text='ℹ️ Эта функция доступна только админстраторам!')


@router.callback_query(lambda x: 'enable_premium' in x.data)
async def process_enable_premium(callback: CallbackQuery):
    tg_id = callback.data.split('-')[1]
    username = callback.data.split('-')[2]
    enable_premium(tg_id)
    keyboard = create_give_premium_keyboard(True, tg_id, username)
    await callback.message.edit_text(text=f'{tg_id} ({username}): Премиум включен')
    await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(lambda x: 'disable_premium' in x.data)
async def process_disable_premium(callback: CallbackQuery):
    tg_id = callback.data.split('-')[1]
    username = callback.data.split('-')[2]
    disable_premium(tg_id)
    keyboard = create_give_premium_keyboard(False, tg_id, username)
    await callback.message.edit_text(text=f'{tg_id} ({username}): Премиум выключен')
    await callback.message.edit_reply_markup(reply_markup=keyboard)
