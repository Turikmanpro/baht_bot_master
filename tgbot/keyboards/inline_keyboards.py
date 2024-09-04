from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.misc import callbacks


def get_back_keyboard(to='main_menu', payload=''):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to=to, payload=payload))
    )

    return keyboard


def get_withdrawal_keyboard(withdrawal_type: str):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Вывести',
                             callback_data=callbacks.navigation.new(to='withdraw_confirm', payload=withdrawal_type))
    )

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='stats', payload=''))
    )

    return keyboard


def get_reviews_keyboard(is_admin: bool, is_completed_deal: bool):
    keyboard = InlineKeyboardMarkup()

    if is_admin:
        keyboard.add(
            InlineKeyboardButton('Удалить отзыв', callback_data='pass')
        )

    if is_completed_deal:
        keyboard.add(
            InlineKeyboardButton('Оставить отзыв', callback_data='pass')
        )

    return keyboard


def get_bank_choose_keyboard(operation_type, back_to, payload='', back_payload=''):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('Тинькофф🏦', callback_data=callbacks.bank_choose.new(bank='Тинькофф', type=operation_type,
                                                                                  payload=payload)),
        InlineKeyboardButton('Сбер🏦', callback_data=callbacks.bank_choose.new(bank='Сбер', type=operation_type,
                                                                              payload=payload)),
        InlineKeyboardButton('Райффайзен🏦',
                             callback_data=callbacks.bank_choose.new(bank='Райффайзен', type=operation_type,
                                                                     payload=payload)),
        InlineKeyboardButton('Другое', callback_data=callbacks.bank_choose.new(bank='Другой', type=operation_type,
                                                                               payload=payload)),
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to=back_to, payload=back_payload))
    )

    return keyboard


def get_operators_keyboard(operators, is_active):
    keyboard = InlineKeyboardMarkup(row_width=2)

    if is_active:
        action = 'delete'
    else:
        action = 'appoint'

    buttons = list()
    for operator in operators:
        buttons.append(
            InlineKeyboardButton(operator.user.name,
                                 callback_data=callbacks.operator_choose.new(id=operator.telegram_id, action=action))
        )
    keyboard.add(*buttons)

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='operators', payload='menu'))
    )

    return keyboard


def get_operator_keyboard(operator_id, action):
    keyboard = InlineKeyboardMarkup(row_width=1)

    if action == 'delete':
        payload = 'active'
        keyboard.add(
            InlineKeyboardButton('Удалить', callback_data=callbacks.operator_update.new(id=operator_id, action=action))
        )
    elif action == 'appoint':
        payload = 'deleted'
        keyboard.add(
            InlineKeyboardButton('Назначить',
                                 callback_data=callbacks.operator_update.new(id=operator_id, action=action))
        )

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='operators', payload=payload))
    )

    return keyboard


def get_referral_level_choose_keyboard(referrals, action, back_to='', back_payload=''):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for referral in referrals:
        keyboard.add(
            InlineKeyboardButton(f'Пользователи {referral.user.name}',
                                 callback_data=callbacks.referral_level_choose.new(level=referral.id, action=action))
        )

    if back_to:
        keyboard.add(
            InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to=back_to, payload=back_payload))
        )

    return keyboard


def get_referral_type_choose_keyboard(level):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('Активные рефералы',
                             callback_data=callbacks.navigation.new(to='active_refs', payload=level)),
        InlineKeyboardButton('Заблокированные рефералы',
                             callback_data=callbacks.navigation.new(to='block_refs', payload=level)),
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='referrals', payload='lvl'))
    )

    return keyboard


def get_referral_choose_keyboard(referrals, action='oper', level=None):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for referral in referrals:
        keyboard.add(
            InlineKeyboardButton(f'{referral.user.name}',
                                 callback_data=callbacks.referral_choose.new(id=referral.telegram_id, action=action))
        )

    if action == 'oper':
        keyboard.add(
            InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='operators', payload='menu'))
        )
    else:
        keyboard.add(
            InlineKeyboardButton('Назад', callback_data=callbacks.referral_level_choose.new(level=level, action='ref'))
        )

    return keyboard


def get_referral_info_keyboard(is_active: bool, level, ref_id):
    keyboard = InlineKeyboardMarkup()

    if is_active:
        to = 'active_refs'
        keyboard.add(InlineKeyboardButton('Заблокировать', callback_data=callbacks.referral_update.new(id=ref_id)))
    else:
        to = 'block_refs'
        keyboard.add(InlineKeyboardButton('Разблокировать', callback_data=callbacks.referral_update.new(id=ref_id)))

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to=to, payload=level))
    )

    return keyboard


def get_referral_update_keyboard(referral_id, is_active: bool, level):
    keyboard = InlineKeyboardMarkup(row_width=1)

    if is_active:
        keyboard.add(
            InlineKeyboardButton('Удалить',
                                 callback_data=callbacks.operator_update.new(id=referral_id, action='delete'))
        )
    else:
        keyboard.add(
            InlineKeyboardButton('Назначить',
                                 callback_data=callbacks.operator_update.new(id=referral_id, action='active'))
        )

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.referral_level_choose.new(level=level, action='oper'))
    )

    return keyboard


def get_order_confirm_keyboard(order_id):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Подтвердить',
                             callback_data=callbacks.operator_order.new(action='confirm', order_id=order_id))
    )

    return keyboard


def get_reviews_link_keyboard(url):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Оставить отзыв', url=url)
    )

    return keyboard


referral_menu = InlineKeyboardMarkup(row_width=1)
referral_menu.add(
    InlineKeyboardButton('Как это работает?', callback_data=callbacks.navigation.new(to='how_works', payload='')),
    InlineKeyboardButton('Моя персональная ссылка', callback_data=callbacks.navigation.new(to='ref_link', payload='')),
    InlineKeyboardButton('Моя статистика', callback_data=callbacks.navigation.new(to='stats', payload=''))
)

statistics_menu = InlineKeyboardMarkup(row_width=1)
statistics_menu.add(
    InlineKeyboardButton('Вывести дивиденды',
                         callback_data=callbacks.navigation.new(to='ref_withdrawal_menu', payload='')),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='ref_menu', payload=''))
)

referral_withdrawal_menu = InlineKeyboardMarkup(row_width=1)
referral_withdrawal_menu.add(
    InlineKeyboardButton('Доставка курьером наличными в THB (Батах)',
                         callback_data=callbacks.navigation.new(to='withdraw', payload='courier')),
    InlineKeyboardButton('Получить на Русский счет в RUB (Рублях)',
                         callback_data=callbacks.navigation.new(to='withdraw', payload='rub')),
    InlineKeyboardButton('Получить на крипто счет в USDT',
                         callback_data=callbacks.navigation.new(to='withdraw', payload='usdt')),
    InlineKeyboardButton('Получить на Тайский счет в THB (Батах)',
                         callback_data=callbacks.navigation.new(to='withdraw', payload='thb')),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='stats', payload=''))
)

token_choose = InlineKeyboardMarkup(row_width=1)
token_choose.add(
    InlineKeyboardButton('TRC20', callback_data=callbacks.token_choose.new(token='TRC20', payload='')),
    InlineKeyboardButton('ERC20', callback_data=callbacks.token_choose.new(token='ERC20', payload='')),
    InlineKeyboardButton('BEP20', callback_data=callbacks.token_choose.new(token='BEP20', payload='')),
    InlineKeyboardButton('BINANCE PAY ID',
                         callback_data=callbacks.token_choose.new(token='BINANCE PAY ID', payload='')),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='withdraw', payload='usdt'))
)



operators_menu = InlineKeyboardMarkup(row_width=1)
operators_menu.add(
    InlineKeyboardButton('Добавить оператора', callback_data=callbacks.navigation.new(to='operators', payload='add')),
    InlineKeyboardButton('Активные операторы',
                         callback_data=callbacks.navigation.new(to='operators', payload='active')),
    InlineKeyboardButton('Удаленные операторы',
                         callback_data=callbacks.navigation.new(to='operators', payload='deleted')),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='admin_menu', payload=''))
)

settings = InlineKeyboardMarkup(row_width=1)
settings.add(
    InlineKeyboardButton('Доставка курьером', callback_data=callbacks.navigation.new(to='delivery_upd', payload='')),
    InlineKeyboardButton('Перевод на счёт', callback_data=callbacks.navigation.new(to='transfer_upd', payload='')),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='admin_menu', payload=''))
)

admin_stats = InlineKeyboardMarkup()
admin_stats.row(
    InlineKeyboardButton('ИР0', callback_data=callbacks.navigation.new(to='ir_stats', payload=0)),
    InlineKeyboardButton('ИР1', callback_data=callbacks.navigation.new(to='ir_stats', payload=1)),
    InlineKeyboardButton('ИР2', callback_data=callbacks.navigation.new(to='ir_stats', payload=2)),
    InlineKeyboardButton('ИР3', callback_data=callbacks.navigation.new(to='ir_stats', payload=3))
)
admin_stats.add(
    InlineKeyboardButton('Отчётные периоды', callback_data=callbacks.navigation.new(to='years', payload='ref')),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='admin_menu', payload=''))
)

admin_menu = InlineKeyboardMarkup(row_width=1)
admin_menu.add(
    InlineKeyboardButton('Статистика', callback_data=callbacks.navigation.new(to='admin_stats', payload='')),
    InlineKeyboardButton('Пользователи', callback_data=callbacks.navigation.new(to='referrals', payload='lvl')),
    InlineKeyboardButton('Операторы', callback_data=callbacks.navigation.new(to='operators', payload='menu')),
    InlineKeyboardButton('Перестановщики', callback_data=callbacks.navigation.new(to='movers', payload=''))
    # InlineKeyboardButton('Настройки', callback_data=callbacks.navigation.new(to='admin_settings', payload=''))
)

cancel_scan = InlineKeyboardMarkup()
cancel_scan.add(
    InlineKeyboardButton('Отмена ввода скана', callback_data='cancel_scan')
)


def get_admin_stat(referrals, start_day):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for referral in referrals:
        keyboard.add(
            InlineKeyboardButton(referral.user.name, callback_data=callbacks.admin_stat.new(referral.id, start_day))
        )

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new('admin_menu', ''))
    )

    return keyboard


order_calc = InlineKeyboardMarkup()
order_calc.add(
    InlineKeyboardButton('Калькулятор сделки', callback_data=callbacks.navigation.new('make_ex', ''))
)
