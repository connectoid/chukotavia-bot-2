from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message


# Клавиатура Главного меню
add_date = KeyboardButton(text='Добавить билет')
watch_date = KeyboardButton(text='Посмотреть билеты')
settings = KeyboardButton(text='Настройки')
help = KeyboardButton(text='Помощь')

main_menu = ReplyKeyboardMarkup(
    keyboard=[[add_date, watch_date],
              [settings, help]],
    resize_keyboard=True
)


# Инлайн-клавиатура выбора направления
prov_anadyr = InlineKeyboardButton(
    text='Провидения - Анадырь',
    callback_data='PVS_DYR'
)

anadyr_prov = InlineKeyboardButton(
    text='Анадырь - Провидения',
    callback_data='DYR_PVS'
)

egv_anadyr = InlineKeyboardButton(
    text='Эгвекинот - Анадырь',
    callback_data='ЭГТ_DYR'
)

anadyr_egv = InlineKeyboardButton(
    text='Анадырь - Эгвекинот',
    callback_data='DYR_ЭГТ'
)

lavr_anadyr = InlineKeyboardButton(
    text='Лаврентия - Анадырь',
    callback_data='ЗЛА_DYR'
)

anadyr_lavr = InlineKeyboardButton(
    text='Анадырь - Лаврентия',
    callback_data='DYR_ЗЛА'
)

direction_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[prov_anadyr],
                     [anadyr_prov],
                     [egv_anadyr],
                     [anadyr_egv],
                     [lavr_anadyr],
                     [anadyr_lavr]]
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
                  

# Инлайн-клавиатура Настройки
def create_everyday_message_keyboard(is_enabled):
    everyday_message_on = InlineKeyboardButton(
        text='Включить',
        callback_data=f'everyday_message_on'
    )

    everyday_message_off = InlineKeyboardButton(
        text='Выключить',
        callback_data=f'everyday_message_off'
    )

    if is_enabled:
        everyday_message_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[everyday_message_off]]
        )
    else:
        everyday_message_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[everyday_message_on]]
        )
    return everyday_message_keyboard
                

# Инлайн-клавиатура Premium
def create_give_premium_keyboard(is_enabled, tg_id, username):
    enable_premium = InlineKeyboardButton(
        text='Дать Premium',
        callback_data=f'enable_premium-{tg_id}-{username}'
    )

    disable_premium = InlineKeyboardButton(
        text='Забрать Premium',
        callback_data=f'disable_premium-{tg_id}-{username}'
    )

    if is_enabled:
        give_premium_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[disable_premium]]
        )
    else:
        give_premium_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[enable_premium]]
        )
    return give_premium_keyboard
                