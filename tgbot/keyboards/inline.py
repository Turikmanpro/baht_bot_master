import datetime
import math

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import tgbot.misc.callbacks as callbacks
from tgbot.services.bitrix.bitrix_schemas import ExchangeType


def get_weeks_keyboard(year, action='oper'):
    keyboard = InlineKeyboardMarkup(row_width=5)

    buttons = []
    for week in range(1, 53 + 1):
        buttons.append(
            InlineKeyboardButton(str(week),
                                 callback_data=callbacks.week_choose.new(year=year, value=week, action=action))
        )

    keyboard.add(*buttons)
    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='years', payload=action))
    )

    return keyboard


def get_years_keyboard(year_start, year_end, action='oper'):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for year in range(year_start, year_end + 1):
        keyboard.add(
            InlineKeyboardButton(str(year), callback_data=callbacks.year_choose.new(year, action=action))
        )

    if action == 'ref':
        keyboard.add(
            InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='admin_stats', payload=''))
        )
    elif action == 'oper':
        keyboard.add(
            InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='operator_menu', payload=''))
        )

    return keyboard


def get_days_keyboard(year, week):
    keyboard = InlineKeyboardMarkup(row_width=1)

    first_day = datetime.datetime(int(year), 1, 1) + datetime.timedelta(days=(int(week) - 1) * 7)
    for day_delta in range(7):
        day = first_day + datetime.timedelta(days=day_delta)
        if day.year != int(year):
            break
        keyboard.add(
            InlineKeyboardButton(day.strftime('%Y-%m-%d'),
                                 callback_data=callbacks.day_choose.new(date=day.strftime('%Y-%m-%d')))
        )

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.year_choose.new(value=year, action='oper'))
    )

    return keyboard


def get_orders_keyboard(orders, date):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for order in orders:
        if order.finished:
            status = 'Выполнен'
        else:
            status = 'Не выполнен'

        button_text = f'{status} - {order.customer_give} {order.exchange_type}'
        keyboard.add(
            InlineKeyboardButton(button_text, callback_data=callbacks.order_choose.new(id=order.bitrix_id))
        )

    keyboard.add(
        InlineKeyboardButton('Назад',
                             callback_data=callbacks.week_choose.new(year=date.year, value=date.isocalendar().week,
                                                                     action='oper'))
    )

    return keyboard


def get_order_keyboard(order_id, give_cur, receive_cur, date):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        # InlineKeyboardButton(f'Сумма к выдаче {receive_cur}', callback_data=callbacks.order_update.new(type='rec', id=order_id)),
        # InlineKeyboardButton(f'Сумма к обмену {give_cur}', callback_data=callbacks.order_update.new(type='give', id=order_id)),
        InlineKeyboardButton(f'Назад', callback_data=callbacks.day_choose.new(date=date))
    )

    return keyboard


def get_courier_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Мои доставки',
                             callback_data=callbacks.navigation.new(to='courier_deliveries', payload='')),
        InlineKeyboardButton('Личный кабинет',
                             callback_data=callbacks.navigation.new(to='courier_account', payload='')),
    )
    keyboard.add(
        InlineKeyboardButton('Закрыть', callback_data='close')
    )

    return keyboard


def get_courier_arrived_keyboard(order_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Прибыл', callback_data=callbacks.courier.new(order_id=order_id, payload='arrived')),
        InlineKeyboardButton('Отказаться', callback_data=callbacks.navigation.new(to='courier_cancel', payload=order_id))
    )
    # keyboard.add(
    #     InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='courier_menu', payload=''))
    # )

    return keyboard


def get_courier_on_the_way_keyboard(order_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('В пути', callback_data=callbacks.courier.new(order_id=order_id, payload='on_the_way')),
        InlineKeyboardButton('Отказаться', callback_data=callbacks.navigation.new(to='courier_cancel', payload=order_id))
    )

    return keyboard


def get_courier_finished_keyboard(order_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Завершено', callback_data=callbacks.courier.new(order_id=order_id, payload='finished'))
    )

    return keyboard


def get_courier_account_keyboard(to_pay: float) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(f'Выплаты - {to_pay} USDT к выдаче',
                             callback_data=callbacks.statistic.new('courier_list', 1))
    )
    # keyboard.add(
    #     InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='courier_menu', payload=''))
    # )

    return keyboard


def get_withdrawal_history(withdrawal_data: list, items_per_page: int, page: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    weeks_to_display = withdrawal_data[(page - 1) * items_per_page:page * items_per_page]
    for week in weeks_to_display:
        keyboard.add(
            InlineKeyboardButton(week['message'],
                                 callback_data=callbacks.withdrawal_history.new(stat_id=week['stat_id']))
        )

    pages_count = math.ceil(len(withdrawal_data) / items_per_page)
    if pages_count > 1:
        next_button = InlineKeyboardButton('>>>', callback_data=callbacks.statistic.new('courier_list', page + 1))
        prev_button = InlineKeyboardButton('<<<', callback_data=callbacks.statistic.new('courier_list', page - 1))

        if page == 1:
            keyboard.add(next_button)
        elif page == pages_count:
            keyboard.add(prev_button)
        else:
            keyboard.add(prev_button, next_button)

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='courier_account', payload=''))
    )

    return keyboard


def get_courier_week_statistic(stat_id: int, courier_status: bool) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    if not courier_status:
        keyboard.add(
            InlineKeyboardButton('Получил(а)', callback_data=callbacks.statistic.new('courier_received', stat_id))
        )

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.statistic.new('courier_list', 1))
    )

    return keyboard


def get_back_keyboard(to: str, payload: str = '') -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to=to, payload=payload))
    )

    return keyboard


def get_operator_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('История заявок',
                             callback_data=callbacks.navigation.new(to='operator_order_list', payload='')),
        InlineKeyboardButton('Курьеры', callback_data=callbacks.navigation.new(to='courier_change_menu', payload=''))
    )
    keyboard.add(
        InlineKeyboardButton('Закрыть', callback_data='close')
    )

    return keyboard


def get_courier_change_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Активные сотрудники',
                             callback_data=callbacks.active_couriers.new(to='active_couriers', telegram_id='',
                                                                         page='1'))
    )

    keyboard.add(
        InlineKeyboardButton('Добавить курьера',
                             callback_data=callbacks.navigation.new(to='add_courier', payload=''))
    )
    # keyboard.add(
    #     InlineKeyboardButton('Удаленные сотрудники',
    #                          callback_data=callbacks.navigation.new(to='deleted_couriers', payload=''))
    # )

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='operator_menu', payload=''))
    )

    return keyboard


def get_choose_original_referral_keyboard(referrals) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    for referral in referrals:
        keyboard.add(
            InlineKeyboardButton(f'Рефералы {referral.user.name}',
                                 callback_data=callbacks.referral_list.new(to='ref_list', original_ref_id=referral.id,
                                                                           page=1, ref_id=''))
        )

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='courier_change_menu', payload=''))
    )

    return keyboard


def get_referrals_list_keyboard(ref_data: list, items_per_page: int, page: int,
                                original_ref_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    refs_to_display = ref_data[(page - 1) * items_per_page:page * items_per_page]
    for ref in refs_to_display:
        keyboard.add(
            InlineKeyboardButton(ref['message'],
                                 callback_data=callbacks.referral_list.new(to='ref_account', ref_id=ref['id'],
                                                                           original_ref_id=original_ref_id, page=page))
        )

    pages_count = math.ceil(len(ref_data) / items_per_page)
    if pages_count > 1:
        next_button = InlineKeyboardButton('>>>', callback_data=callbacks.referral_list.new(to='ref_list', ref_id='',
                                                                                            original_ref_id=original_ref_id,
                                                                                            page=page + 1))
        prev_button = InlineKeyboardButton('<<<', callback_data=callbacks.referral_list.new(to='ref_list', ref_id='',
                                                                                            original_ref_id=original_ref_id,
                                                                                            page=page - 1))

        if page == 1:
            keyboard.add(next_button)
        elif page == pages_count:
            keyboard.add(prev_button)
        else:
            keyboard.add(prev_button, next_button)

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='add_courier', payload=''))
    )

    return keyboard


def get_ref_account_keyboard(to, ref_id, original_ref_id, page, will_be_courier, telegram_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    if will_be_courier:
        message = 'Назначить курьером'
    else:
        message = 'Удалить из курьеров'
    keyboard.add(
        InlineKeyboardButton(message, callback_data=callbacks.referral_list.new(to='update_courier', ref_id=telegram_id,
                                                                                original_ref_id='', page=''))
    )

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.referral_list.new(
            to=to,
            ref_id=ref_id,
            original_ref_id=original_ref_id,
            page=page))
    )

    return keyboard


def get_active_couriers_list(couriers: list, items_per_page: int, page: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    couriers_to_display = couriers[(page - 1) * items_per_page:page * items_per_page]
    for courier in couriers_to_display:
        keyboard.add(
            InlineKeyboardButton(courier['name'], callback_data=callbacks.active_couriers.new(to='courier',
                                                                                              telegram_id=courier[
                                                                                                  'telegram_id'],
                                                                                              page=page))
        )

    pages_count = math.ceil(len(couriers) / items_per_page)
    if pages_count > 1:
        next_button = InlineKeyboardButton('>>>', callback_data=callbacks.active_couriers.new(to='active_couriers',
                                                                                              telegram_id='',
                                                                                              page=page + 1))
        prev_button = InlineKeyboardButton('<<<', callback_data=callbacks.active_couriers.new(to='active_couriers',
                                                                                              telegram_id='',
                                                                                              page=page - 1))

        if page == 1:
            keyboard.add(next_button)
        elif page == pages_count:
            keyboard.add(prev_button)
        else:
            keyboard.add(prev_button, next_button)

    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='courier_change_menu', payload=''))
    )

    return keyboard


def get_active_courier_info_keyboard(is_admin: bool, withdrawal_amount: float, page: int,
                                     telegram_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    if is_admin:
        keyboard.add(
            InlineKeyboardButton('Удалить курьера', callback_data=callbacks.active_couriers.new(to='del_active_courier',
                                                                                                telegram_id=telegram_id,
                                                                                                page=page))
        )

    keyboard.add(
        InlineKeyboardButton(f'Выплаты - {withdrawal_amount} USDT',
                             callback_data=callbacks.active_couriers.new(to='withdrawal', telegram_id=telegram_id,
                                                                         page=1))
    )
    keyboard.add(
        InlineKeyboardButton('История заявок', callback_data=callbacks.active_couriers.new(to='withdrawal_history',
                                                                                           telegram_id=telegram_id,
                                                                                           page=page))
    )
    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.active_couriers.new(to='active_couriers', telegram_id='',
                                                                                  page=page))
    )

    return keyboard


def get_courier_withdrawal_stat_list_keyboard(deals_count_info: list, telegram_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(f'Купить наличные THB за безналичные RUB - {deals_count_info[0]}',
                             callback_data=callbacks.active_couriers.new(to='rub/thb', telegram_id=telegram_id,
                                                                         page=1))
    )
    keyboard.add(
        InlineKeyboardButton(f'Купить безналичные RUB за наличные THB - {deals_count_info[1]}',
                             callback_data=callbacks.active_couriers.new(to='thb/rub', telegram_id=telegram_id,
                                                                         page=1))
    )
    keyboard.add(
        InlineKeyboardButton(f'Купить USDT за наличные THB - {deals_count_info[2]}',
                             callback_data=callbacks.active_couriers.new(to='thb/usdt', telegram_id=telegram_id,
                                                                         page=1))
    )
    keyboard.add(
        InlineKeyboardButton(f'Купить наличные THB за USDT - {deals_count_info[3]}',
                             callback_data=callbacks.active_couriers.new(to='usdt/thb', telegram_id=telegram_id, page=1))
    )
    keyboard.add(
        InlineKeyboardButton('Назад',
                             callback_data=callbacks.active_couriers.new(to='courier', telegram_id=telegram_id,
                                                                         page=1))
    )

    return keyboard


def get_courier_deal_list(pages_count: int, page: int, telegram_id: int, to: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    if pages_count > 1:
        next_button = InlineKeyboardButton('>>>',
                                           callback_data=callbacks.active_couriers.new(
                                               to=to,
                                               telegram_id=telegram_id,
                                               page=page + 1
                                           ))
        prev_button = InlineKeyboardButton('<<<',
                                           callback_data=callbacks.active_couriers.new(
                                               to=to,
                                               telegram_id=telegram_id,
                                               page=page - 1
                                           ))

        if page == 1:
            keyboard.add(next_button)
        elif page == pages_count:
            keyboard.add(prev_button)
        else:
            keyboard.add(prev_button, next_button)

    keyboard.add(
        InlineKeyboardButton('Назад',
                             callback_data=callbacks.active_couriers.new(
                                 to='withdrawal_history',
                                 telegram_id=telegram_id,
                                 page=1
                             ))
    )

    return keyboard


def get_active_courier_withdrawal(withdrawal_data: list, items_per_page: int, page: int,
                                  telegram_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    weeks_to_display = withdrawal_data[(page - 1) * items_per_page:page * items_per_page]
    for week in weeks_to_display:
        keyboard.add(
            InlineKeyboardButton(week['message'],
                                 callback_data=callbacks.active_couriers.new(
                                     to='week_info',
                                     telegram_id=telegram_id,
                                     page=week['stat_id']
                                 ))
        )

    pages_count = math.ceil(len(withdrawal_data) / items_per_page)
    if pages_count > 1:
        next_button = InlineKeyboardButton('>>>',
                                           callback_data=callbacks.active_couriers.new(
                                               to='withdrawal',
                                               telegram_id=telegram_id,
                                               page=page + 1
                                           ))
        prev_button = InlineKeyboardButton('<<<',
                                           callback_data=callbacks.active_couriers.new(
                                               to='withdrawal',
                                               telegram_id=telegram_id,
                                               page=page - 1
                                           ))
        if page == 1:
            keyboard.add(next_button)
        elif page == pages_count:
            keyboard.add(prev_button)
        else:
            keyboard.add(prev_button, next_button)

    keyboard.add(
        InlineKeyboardButton('Назад',
                             callback_data=callbacks.active_couriers.new(to='courier', telegram_id=telegram_id, page=1))
    )

    return keyboard


def get_courier_week_statistic_for_operator(stat_id: int, operator_status: bool,
                                            telegram_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    if not operator_status:
        keyboard.add(
            InlineKeyboardButton('Выплачено',
                                 callback_data=callbacks.active_couriers.new(to='courier_paid', page=stat_id,
                                                                             telegram_id=telegram_id))
        )

    keyboard.add(
        InlineKeyboardButton('Назад',
                             callback_data=callbacks.active_couriers.new(to='withdrawal', telegram_id=telegram_id,
                                                                         page=1))
    )

    return keyboard


def get_notify_keyboard(order_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Обновить курс', callback_data=callbacks.crm_notify.new(order_id, 'update_rate')),
        # InlineKeyboardButton('Сообщить о проблеме', callback_data=callbacks.customer_order.new(order_id, 'problem'))
    )

    return keyboard


def get_input_requisites(order_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Ввести реквизиты', callback_data=callbacks.crm_notify.new(order_id, 'confirm_update'))
    )

    return keyboard


def get_couriers_choose(couriers: list, order_id) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)

    for i in couriers:
        keyboard.add(
            InlineKeyboardButton(text=i['name'], callback_data=callbacks.courier_choose.new(order_id, i['telegram_id']))
        )
    return keyboard


def get_client_change_order_sum(order_id, cur1, cur2) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(f'Сумма в {cur1}', callback_data=callbacks.client_change.new('change', order_id, cur1)),
        InlineKeyboardButton(f'Сумма в {cur2}', callback_data=callbacks.client_change.new('change', order_id, cur2)),
        InlineKeyboardButton('Оставить без изменений', callback_data=callbacks.client_change.new('stay', order_id, ''))
    )

    return keyboard


def get_problem_accepted_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('Закрыть', callback_data='close')
    )
    return keyboard


def get_operator_order_keyboard(order_id):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('Проверить',
                             callback_data=callbacks.operator_order.new(order_id=order_id, action='check')),
        InlineKeyboardButton('Взяться', callback_data=callbacks.operator_order.new(order_id=order_id, action='take'))
    )

    return keyboard


def get_customer_order_keyboard(order_id):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('Загрузить чек 🧾',
                             callback_data=callbacks.customer_order.new(order_id=order_id, action='load')),
        InlineKeyboardButton('У меня проблема',
                             callback_data=callbacks.customer_order.new(order_id=order_id, action='problem'))
    )

    return keyboard


def get_send_scan(order_id):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Загрузить чек 🧾',
                             callback_data=callbacks.customer_order.new(order_id=order_id, action='load'))
    )

    return keyboard


def get_delivery_confirm_keyboard(order_id):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Выдача', callback_data=callbacks.courier_order.new(order_id=order_id))
    )

    return keyboard


def get_receive_confirm_keyboard(order_id, show_problem=True):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Получил(а)', callback_data=callbacks.crm_notify.new(order_id, 'ok'))
    )

    if show_problem:
        keyboard.add(
            InlineKeyboardButton('У меня проблема',
                                 callback_data=callbacks.customer_order.new(order_id=order_id, action='problem2'))
        )

    return keyboard


def get_problem_solved_keyboard(order_id, first=True):
    keyboard = InlineKeyboardMarkup()

    if first:
        callback = 'solv_problem'
    else:
        callback = 'solv_problem2'

    keyboard.add(
        InlineKeyboardButton('Проблема решена', callback_data=callbacks.crm_notify.new(order_id, callback))
    )
    return keyboard


courier_menu = InlineKeyboardMarkup(row_width=1)
courier_menu.add(
    InlineKeyboardButton('Мои доставки', callback_data=callbacks.navigation.new(to='courier_deliveries', payload='')),
    InlineKeyboardButton('Личный кабинет', callback_data=callbacks.navigation.new(to='courier_account', payload='')),
)

operator_menu = InlineKeyboardMarkup(row_width=1)
operator_menu.add(
    InlineKeyboardButton('История заявок', callback_data=callbacks.navigation.new(to='order_list', payload='')),
    InlineKeyboardButton('Курьеры', callback_data=callbacks.navigation.new(to='courier_change_menu', payload='')),
    InlineKeyboardButton('Текущие заказы', callback_data=callbacks.navigation.new(to='active_orders', payload=''))
)


def get_active_orders_list(orders):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for order in orders:
        order = order[0]
        print(order)
        keyboard.add(
            InlineKeyboardButton(f'{order.bitrix_id} {order.customer_name}', callback_data=callbacks.navigation.new(to='active_order_info', payload=order.bitrix_id))
        )
    keyboard.add(
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='operator_menu', payload=''))
    )
    return keyboard


def get_cancel_order_menu(order_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton('Отменить заказ', callback_data=callbacks.navigation.new(to='cancel_order', payload=order_id)),
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='active_orders', payload=''))
    )
    return keyboard
