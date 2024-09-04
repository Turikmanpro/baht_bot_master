import math

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.misc import callbacks

choose_permutation = InlineKeyboardMarkup()
choose_permutation.add(
    InlineKeyboardButton('Калькулятор сделки', callback_data=callbacks.navigation.new('permut_deal_calc', '')),
    InlineKeyboardButton('Оформить быструю сделку', callback_data=callbacks.navigation.new('permut_quick_deal', ''))
)

choose_currency = InlineKeyboardMarkup()
choose_currency.add(
    InlineKeyboardButton('RUB', callback_data=callbacks.navigation.new('choose_cur', 'RUB')),
    InlineKeyboardButton('USD', callback_data=callbacks.navigation.new('choose_cur', 'USD'))
)

choose_type = InlineKeyboardMarkup()
choose_type.add(
    InlineKeyboardButton('Безналичные', callback_data=callbacks.navigation.new('choose_type', 'non-cash')),
    InlineKeyboardButton('Наличные', callback_data=callbacks.navigation.new('choose_type', 'cash'))
)

confirm_quick_deal = InlineKeyboardMarkup()
confirm_quick_deal.add(
    InlineKeyboardButton('Отправить заявку', callback_data=callbacks.navigation.new('quick_confirm', 'yes')),
    InlineKeyboardButton('Отмена', callback_data=callbacks.navigation.new('quick_confirm', 'no'))
)

mover_menu = InlineKeyboardMarkup(row_width=1)
mover_menu.add(
    InlineKeyboardButton('Добавить перестановщика', callback_data=callbacks.movers.new('add_menu', '')),
    InlineKeyboardButton('Активные перестановщики', callback_data=callbacks.movers.new('active', '1')),
    InlineKeyboardButton('Удаленные перестановщики', callback_data=callbacks.movers.new('deleted', '1')),
    # InlineKeyboardButton('История заявок', callback_data=callbacks.movers.new('order_history', '')),
    InlineKeyboardButton('Текущие заказы', callback_data=callbacks.movers.new('orders_now', '')),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new('admin_menu', ''))
)

often_deal_receiving_office = InlineKeyboardMarkup(row_width=1)
often_deal_receiving_office.add(
    InlineKeyboardButton('г.Москва', callback_data=callbacks.navigation.new('receiving_office', 'msk')),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new('permut_deal_calc', ''))
)

often_deal_country_choose = InlineKeyboardMarkup(row_width=1)
often_deal_country_choose.add(
    InlineKeyboardButton('Тайланд', callback_data=callbacks.navigation.new('often_country_choose', 'tai')),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new('choose_cur', ''))
)

often_deal_city_choose = InlineKeyboardMarkup(row_width=1)
often_deal_city_choose.add(
    InlineKeyboardButton('Пхукет', callback_data=callbacks.navigation.new('often_city_choose', 'ph')),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new('choose_type', ''))
)

back_to_mover_admin = InlineKeyboardMarkup()
back_to_mover_admin.add(
    InlineKeyboardButton('Назад', callback_data=callbacks.movers.new('orders_now', ''))
)


def get_mover_orig_referral_keyboard(orig_ref_ids: list) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for i in orig_ref_ids:
        if i == 0:
            m = ' Дефолтный'
        else:
            m = i
        keyboard.add(InlineKeyboardButton(f'Пользователи ИР{m}',
                                          callback_data=callbacks.movers_orig_ref_choose.new(str(i), '1')))
    keyboard.add(InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new('movers', '')))
    return keyboard


def get_mover_ref_list_keyboard(referrals: list, items_per_page: int, page: int, action: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    referrals_to_display = referrals[(page - 1) * items_per_page:page * items_per_page]
    for referral in referrals_to_display:
        keyboard.add(
            InlineKeyboardButton(referral['name'],
                                 callback_data=callbacks.movers_update.new(action, referral['id']))
        )

    pages_count = math.ceil(len(referrals) / items_per_page)
    if pages_count > 1:
        if action == 'add':
            orig_ref_id = referrals[0]['orig_ref_id']
            next_button = InlineKeyboardButton('>>>',
                                               callback_data=callbacks.movers_orig_ref_choose.new(orig_ref_id,
                                                                                                  page + 1))
            prev_button = InlineKeyboardButton('<<<',
                                               callback_data=callbacks.movers_orig_ref_choose.new(orig_ref_id,
                                                                                                  page - 1))
        elif action in ('deleted', 'active'):
            next_button = InlineKeyboardButton('>>>',
                                               callback_data=callbacks.movers.new(action,
                                                                                  page + 1))
            prev_button = InlineKeyboardButton('<<<',
                                               callback_data=callbacks.movers_orig_ref_choose.new(action,
                                                                                                  page - 1))

        if page == 1:
            keyboard.add(next_button)
        elif page == pages_count:
            keyboard.add(prev_button)
        else:
            keyboard.add(prev_button, next_button)
    if action == 'add':
        keyboard.add(InlineKeyboardButton('Назад', callback_data=callbacks.movers.new('add_menu', '')))
    elif action in ('deleted', 'active'):
        keyboard.add(InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new('movers', '')))
    return keyboard


def get_referral_update_keyboard(user, is_active: bool, action: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    if is_active:
        keyboard.add(
            InlineKeyboardButton('Удалить', callback_data=callbacks.movers.new('update_mover', user.telegram_id)))
    else:
        keyboard.add(
            InlineKeyboardButton('Назначить', callback_data=callbacks.movers.new('update_mover', user.telegram_id)))
    if action == 'add':
        keyboard.add(InlineKeyboardButton('Назад', callback_data=callbacks.movers_orig_ref_choose.new(
            user.referral.original_referral_id, 1)))
    elif action in ('deleted', 'active'):
        keyboard.add(InlineKeyboardButton('Назад', callback_data=callbacks.movers.new(action, '1')))
    return keyboard


def get_mover_order_keyboard(mover_order_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('Проверить',
                             callback_data=callbacks.movers_order.new(order_id=mover_order_id, action='check')),
        InlineKeyboardButton('Взяться',
                             callback_data=callbacks.movers_order.new(order_id=mover_order_id, action='take'))
    )

    return keyboard


def get_active_movers_order(mover_orders: list) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)

    for i in mover_orders:
        keyboard.add(
            InlineKeyboardButton(i['name'], callback_data=callbacks.movers_order.new(order_id=i['id'], action='show'))
        )
    keyboard.add(InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new('movers', '')))
    return keyboard
