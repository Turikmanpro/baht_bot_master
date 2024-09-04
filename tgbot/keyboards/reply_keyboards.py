from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.misc import reply_commands

get_phone = ReplyKeyboardMarkup(resize_keyboard=True)
get_phone.add(
    KeyboardButton('Отправить телефон📱', request_contact=True),
    KeyboardButton('Отмена')
)

get_location = ReplyKeyboardMarkup(resize_keyboard=True)
get_location.add(
    KeyboardButton('Отправить свою геопозицию', request_location=True),
    KeyboardButton('Отмена')
)

bank_choose = ReplyKeyboardMarkup(resize_keyboard=True)
bank_choose.add(
    KeyboardButton('Тинькофф'),
    KeyboardButton('Сбер'),
    KeyboardButton('Райффайзен'),
    KeyboardButton('Другое'),
    KeyboardButton('Отмена')
)

cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add(
    KeyboardButton('Отмена')
)

exchange_cancel_with_sum = ReplyKeyboardMarkup(resize_keyboard=True)
exchange_cancel_with_sum.add(
    KeyboardButton('500'),
    KeyboardButton('1000'),
    KeyboardButton('3000'),
    KeyboardButton('5000'),
    KeyboardButton('10000'),
    KeyboardButton('100000'),
    KeyboardButton('Отмена')
)

exchange_cancel_with_sum_thb = ReplyKeyboardMarkup(resize_keyboard=True)
exchange_cancel_with_sum_thb.add(
    KeyboardButton('5000'),
    KeyboardButton('10000'),
    KeyboardButton('30000'),
    KeyboardButton('50000'),
    KeyboardButton('100000'),
    KeyboardButton('Отмена')
)


def get_main_keyboard(show_reg_button: bool, is_courier: bool):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    keyboard.add(
        KeyboardButton(reply_commands.exchange_rate), KeyboardButton(reply_commands.referral_menu),
        KeyboardButton(reply_commands.make_exchange), KeyboardButton(reply_commands.support),
        KeyboardButton(reply_commands.rent), KeyboardButton(reply_commands.reviews),
        KeyboardButton(reply_commands.permutations), KeyboardButton(reply_commands.about)
    )

    if is_courier:
        keyboard.add(
            KeyboardButton(reply_commands.courier_account),
            KeyboardButton(reply_commands.courier_deliveries)
        )

    if show_reg_button:
        keyboard.add(
            KeyboardButton(reply_commands.registration)
        )

    return keyboard
