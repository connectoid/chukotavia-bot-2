from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from keyboards.keyboards import main_menu, direction_keyboard, yes_no_keyboard, create_del_request_keyboard
from database.orm import add_user, add_ticket, get_tickets, delete_ticket, get_ticket_by_id
from service.tools import check_and_convert_date, request_tickets

router = Router()
storage = MemoryStorage()

class FSMAddDate(StatesGroup):
    add_date = State()
    add_direction = State()

date_dict = {}
directions = {
    'PVS_DYR': 'Провидения - Анадырь',
    'DYR_PVS': 'Анадырь - Провидения',
}


@router.message(CommandStart(), StateFilter(default_state))
async def proccess_start_command(message: Message):
    response = add_user(message.from_user.id, message.from_user.username)
    print(response)
    await message.answer('Приветствую. Вы запустили бот, который мониторит наличие в продаже билетов '
                         'авиакомпании Чукотавиа на заданные маршрут и дату. Краткую инструкцию по работе '
                         'с ботом можно посмотреть в разделе Помощь в главном меню или выполнив команду /help.',
                         reply_markup=main_menu)
    

@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text='Отменять нечего. Вы не в процессе добавления даты\n',
                         reply_markup=main_menu)
    

@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text='Вы вышли из процесса добавления даты\n\n',
                         reply_markup=main_menu)
    await state.clear()


@router.message(Command(commands='adddate'), StateFilter(default_state))
@router.message(F.text == 'Добавить дату', StateFilter(default_state))
async def process_adddate_command(message: Message, state: FSMContext):
    await message.answer(text='Пожалуйста, введите дату в формате ДД.ММ.ГГГГ',
                         show_alert=False)
    await state.set_state(FSMAddDate.add_date)


@router.callback_query(F.data == 'yes', StateFilter(default_state))
async def process_adddate_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='Пожалуйста, введите дату в формате ДД.ММ.ГГГГ')
    await state.set_state(FSMAddDate.add_date)
    

# Этот хэндлер будет срабатывать, если введена корректная дата
# и переводить в состояние ожидания ввода направления
@router.message(StateFilter(FSMAddDate.add_date), ~F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенную дату в хранилище по ключу "date"
    if check_and_convert_date(message.text):
        await state.update_data(date=message.text)
        await message.answer(text='Спасибо!\nА теперь выберите направление',
                            reply_markup=direction_keyboard)
        # Устанавливаем состояние ожидания ввода направления
        await state.set_state(FSMAddDate.add_direction)
    else:
        await message.answer(text='Вы ввели дату в неправильном формате или несуществующую дату\n'
                             'Пожалйста, введите дату в формате ДД.ММ.ГГГГ\n'
                             'Если вы хотите прервать добавление даты - '
                             'отправьте команду /cancel')


# Этот хэндлер будет срабатывать, если во время ввода даты
# будет введено что-то некорректное
@router.message(StateFilter(FSMAddDate.add_date))
async def warning_not_date(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на дату\n'
             'Пожалуйста, введите дату в формате ДД.ММ.ГГГГ\n'
             'Если вы хотите прервать добавление даты - '
             'отправьте команду /cancel'
    )


@router.callback_query(F.data == 'PVS_DYR')
@router.callback_query(F.data == 'DYR_PVS')
async def process_direction_sent(callback: CallbackQuery, state: FSMContext):
    # Cохраняем введенное направление в хранилище по ключу "direction"
    await state.update_data(direction=callback.data)
    date_dict[callback.from_user.id] = await state.get_data()
    await state.clear()
    # Отправляем в чат сообщение о выходе из машины состояний
    direction_ru = directions[date_dict[callback.from_user.id]["direction"]]
    direction_en = date_dict[callback.from_user.id]["direction"]
    date = date_dict[callback.from_user.id]["date"]
    add_ticket(callback.from_user.id, date, direction_en)
    await callback.message.edit_text(
        text='Спасибо! Ваши данные сохранены!\n'
             f'Добавлен монитторинг билетов на {date} по маршруту {direction_ru}\n'
             'Добавить еще одну дату?',
             reply_markup=yes_no_keyboard, row_width = 2)
    

@router.message(StateFilter(FSMAddDate.add_direction))
async def warning_not_direction(message: Message):
    await message.answer(
        text='Пожалуйста, воспользуйтесь кнопками для выбора направления!\n'
             'Если вы хотите прервать добавление даты - '
             'отправьте команду /cancel',
             reply_markup=direction_keyboard
    )


@router.callback_query(F.data == 'no')
async def process_direction_exit(callback: CallbackQuery, state: FSMContext):
    # await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        text='Спасибо! Вы вышли из процесса добавления даты\n',
             reply_markup=main_menu)


@router.message(Command(commands='help'))
@router.message(F.text == 'Помощь', StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(text='Здесь будет справочная информация', 
                         reply_markup=main_menu)


@router.message(Command(commands='gettickets'))
@router.message(F.text == 'Посмотреть даты')
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
        await message.answer(text=f'У вас еще не добавлено ни одной даты', 
                                reply_markup=main_menu)
        
    
@router.callback_query(lambda x: 'delete_' in x.data)
async def process_delete_ticket(callback: CallbackQuery):
    # await callback.message.delete()
    ticket_id = callback.data.split('_')[1]
    delete_ticket(ticket_id)
    await callback.message.answer(
        text='Дата удалена из мониторинга\n',
             reply_markup=main_menu)


@router.callback_query(lambda x: 'request_' in x.data)
async def process_request_ticket(callback: CallbackQuery):
    # await callback.message.delete()
    ticket_id = callback.data.split('_')[1]
    ticket = get_ticket_by_id(ticket_id)
    ticket_message = request_tickets(ticket.date, ticket.direction)
    await callback.message.answer(
        text=ticket_message,
             reply_markup=main_menu)