from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from keyboards.keyboards import main_menu, direction_keyboard, yes_no_keyboard
from database.orm import add_user 

router = Router()
storage = MemoryStorage()

class FSMAddDate(StatesGroup):
    add_date = State()
    add_direction = State()

date_dict = {}
directions = {
    'prov_anadyr': 'Провидения - Анадырь',
    'anadyr_prov': 'Анадырь - Провидения',
}


@router.message(CommandStart(), StateFilter(default_state))
async def proccess_start_command(message: Message):
    response = add_user(message.from_user.id, message.from_user.username)
    print(response)
    await message.answer('Приветствую. Вы запустили бот, который мониторит наличие в продаже билетов '
                         'авиакомпании Чукотавиа на заданные маршрут и дату. Краткая инструкция по работе '
                         'с ботом находится в разделе Справка в главном меню.',
                         reply_markup=main_menu)
    

@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text='Отменять нечего. Вы не в процессе добавления билета\n',
                         reply_markup=main_menu)
    

@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text='Вы вышли из процесса добавления билета\n\n',
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
    # await state.clear()
    # await callback.message.delete()
    await callback.message.edit_text(
        text='Пожалуйста, введите дату в формате ДД.ММ.ГГГГ')
    await state.set_state(FSMAddDate.add_date)
    

# Этот хэндлер будет срабатывать, если введена корректная дата
# и переводить в состояние ожидания ввода направления
@router.message(StateFilter(FSMAddDate.add_date), ~F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенную дату в хранилище по ключу "date"
    await state.update_data(date=message.text)
    await message.answer(text='Спасибо!\nА теперь выберите направление',
                         reply_markup=direction_keyboard)
    # Устанавливаем состояние ожидания ввода направления
    await state.set_state(FSMAddDate.add_direction)


# Этот хэндлер будет срабатывать, если во время ввода даты
# будет введено что-то некорректное
@router.message(StateFilter(FSMAddDate.add_date))
async def warning_not_date(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на дату\n'
             'Пожалуйста, введите дату в формате ДД.ММ.ГГГ\n'
             'Если вы хотите прервать добавление даты - '
             'отправьте команду /cancel'
    )


@router.callback_query(F.data == 'prov_anadyr')
@router.callback_query(F.data == 'anadyr_prov')
async def process_direction_sent(callback: CallbackQuery, state: FSMContext):
    # Cохраняем введенное направление в хранилище по ключу "direction"
    await state.update_data(direction=callback.data)
    date_dict[callback.from_user.id] = await state.get_data()
    await state.clear()
    # Отправляем в чат сообщение о выходе из машины состояний
    direction_ru = directions[date_dict[callback.from_user.id]["direction"]]
    await callback.message.edit_text(
        text='Спасибо! Ваши данные сохранены!\n'
             f'Добавлен билет на {date_dict[callback.from_user.id]["date"]} по маршруту {direction_ru}\n'
             'Добавить еще одну дату?',
             reply_markup=yes_no_keyboard)
    

@router.message(StateFilter(FSMAddDate.add_direction))
async def warning_not_direction(message: Message):
    await message.answer(
        text='Пожалуйста, воспользуйтесь кнопками для выбора направления!\n'
             'Если вы хотите прервать добавление билетп - '
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
    await message.answer(text='Здесь будет справочная информация', 
                         reply_markup=main_menu)