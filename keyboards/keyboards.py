from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message


# Клавиатура Главного меню
add_date = KeyboardButton(text='Добавить дату')
watch_date = KeyboardButton(text='Посмотреть даты')
settings = KeyboardButton(text='Настройки')
help = KeyboardButton(text='Помощь')

main_menu = ReplyKeyboardMarkup(
    keyboard=[[add_date, watch_date],
              [settings, help]],
    resize_keyboard=True
)


# Инлайн-клавиатура выбора направления
prov_anadyr = InlineKeyboardButton(
    text='Провидения 🛫 Анадырь',
    callback_data='PVS_DYR'
)

anadyr_prov = InlineKeyboardButton(
    text='Анадырь 🛫 Провидения',
    callback_data='DYR_PVS'
)

direction_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[prov_anadyr],
                     [anadyr_prov]]
)


# Инлайн-клавиатура Да/Нет
yes = InlineKeyboardButton(
    text='Да',
    callback_data='yes'
)

no = InlineKeyboardButton(
    text='Нет',
    callback_data='no'
)

yes_no_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[yes],[no]],
    row_width=2
)


# Инлайн-клавиатура удаления и запроса билета по дате
def create_del_request_keyboard(ticket_id):
    delete = InlineKeyboardButton(
        text='Удалить',
        callback_data=f'delete_{ticket_id}'
    )

    request = InlineKeyboardButton(
        text='Проверить',
        callback_data=f'request_{ticket_id}'
    )

    del_request_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[delete],[request]],
        row_width=2
    )
    return del_request_keyboard
                  