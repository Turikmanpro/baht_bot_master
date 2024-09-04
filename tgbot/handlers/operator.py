import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils import markdown as md
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import tgbot.keyboards.inline as inline_keyboards
import tgbot.misc.callbacks as callbacks
import tgbot.misc.messages as messages
from tgbot.handlers.courier import get_courier_stat_message
from tgbot.handlers.exchange import get_custom_fields
from tgbot.keyboards import reply_keyboards
from tgbot.keyboards.inline_keyboards import get_order_confirm_keyboard
from tgbot.misc import reply_commands, states
from tgbot.misc.helper import is_canceled
from tgbot.services.bitrix.bitrix_schemas import DealType, ExchangeType
from tgbot.services.database.models import Courier, Order, Statistic, User
from tgbot.services.database.models.referral import Referral


async def courier_change_menu(call: CallbackQuery):
    await call.message.edit_text('Курьеры', reply_markup=inline_keyboards.get_courier_change_menu_keyboard())
    await call.answer()


async def send_courier_change_menu(message: Message):
    await message.answer('Курьеры', reply_markup=inline_keyboards.get_courier_change_menu_keyboard())


async def send_operator_order_list(message: Message):
    db_session = message.bot.get('database')
    async with db_session() as session:
        first_week = (await session.execute(
            'SELECT week_created_at FROM statistic ORDER BY week_created_at ASC LIMIT 1')).scalar()
        last_week = (await session.execute(
            'SELECT week_created_at FROM statistic ORDER BY week_created_at DESC LIMIT 1')).scalar()

    await message.answer('Выберите год',
                         reply_markup=inline_keyboards.get_years_keyboard(first_week.year, last_week.year))


async def show_operator_order_list(call: CallbackQuery):
    db_session = call.bot.get('database')
    async with db_session() as session:
        first_week = (await session.execute(
            'SELECT week_created_at FROM statistic ORDER BY week_created_at ASC LIMIT 1')).scalar()
        last_week = (await session.execute(
            'SELECT week_created_at FROM statistic ORDER BY week_created_at DESC LIMIT 1')).scalar()
    if first_week:
        await call.message.edit_text('Выберите год',
                                     reply_markup=inline_keyboards.get_years_keyboard(first_week.year, last_week.year))
        await call.answer()
    else:
        await call.answer('Нет доступных периодов', show_alert=True)


async def show_years_choose(call: CallbackQuery, callback_data: dict):
    db_session = call.bot.get('database')
    async with db_session() as session:
        first_week = (await session.execute(
            'SELECT week_created_at FROM statistic ORDER BY week_created_at ASC LIMIT 1')).scalar()
        last_week = (await session.execute(
            'SELECT week_created_at FROM statistic ORDER BY week_created_at DESC LIMIT 1')).scalar()
    if first_week:
        await call.message.edit_text('Выберите год',
                                     reply_markup=inline_keyboards.get_years_keyboard(first_week.year, last_week.year,
                                                                                      action=callback_data['payload']))
        await call.answer()
    else:
        await call.answer('Нет доступных периодов', show_alert=True)


async def show_weeks(call: CallbackQuery, callback_data: dict):
    await call.message.edit_text(
        'Выберите неделю',
        reply_markup=inline_keyboards.get_weeks_keyboard(callback_data['value'], action=callback_data['action'])
    )
    await call.answer()


async def show_days(call: CallbackQuery, callback_data: dict):
    await call.message.edit_text(
        'Выберите день',
        reply_markup=inline_keyboards.get_days_keyboard(callback_data['year'], callback_data['value'])
    )
    await call.answer()


async def show_orders(call: CallbackQuery, callback_data: dict):
    day = datetime.datetime.strptime(callback_data['date'], '%Y-%m-%d')
    db_session = call.bot.get('database')
    async with db_session() as session:
        orders = await session.execute(
            f"SELECT * FROM bitrix_order WHERE started_at BETWEEN '{day}' AND '{day + datetime.timedelta(hours=23, minutes=59)}'")
        orders = orders.all()

    if not orders:
        await call.answer('Заявок в этот день нет!', show_alert=True)
        return

    await call.message.edit_text('Выберите заявку', reply_markup=inline_keyboards.get_orders_keyboard(orders, day))
    await call.answer()


async def show_order(call: CallbackQuery, callback_data: dict):
    order_id = callback_data['id']

    db_session = call.bot.get('database')
    async with db_session() as session:
        order = await session.get(Order, int(order_id))

    give_cur, rec_cur = map(str.strip, order.exchange_type.split('/'))
    await call.message.edit_text(
        messages.order.format(
            bitrix_id=order.bitrix_id,
            exchange_type=order.exchange_type,
            username=order.customer_name,
            customer_telegram_id=order.customer_telegram_id,
            phone_number=order.phone_number,
            receive_cur=rec_cur,
            customer_receive=order.customer_receive,
            give_cur=give_cur,
            customer_give=order.customer_give,
            exchange_rate=order.exchange_rate,
            location=order.location,
            started_at=order.started_at
        ),
        reply_markup=inline_keyboards.get_order_keyboard(order_id, give_cur, rec_cur, str(order.started_at).split()[0])
    )
    await call.answer()


async def start_sum_input(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.answer('Введите сумму:', reply_markup=reply_keyboards.cancel)

    await states.OrderUpdateState.waiting_for_value.set()
    await state.update_data(order_id=callback_data['id'], type=callback_data['type'])
    await call.answer()


async def get_sum(message: Message, state: FSMContext):
    new_sum = message.text
    if not new_sum.isdigit():
        await message.answer('Неверная сумма, попробуйте ещё раз:')
        return

    async with state.proxy() as data:
        order_id = data['order_id']
        sum_type = data['type']

    db_session = message.bot.get('database')
    async with db_session.begin() as session:
        order = await session.get(Order, int(order_id))
        user = await session.get(User, message.from_id)
        if sum_type == 'give':
            order.customer_give = int(new_sum)
        elif sum_type == 'rec':
            order.customer_receive = int(new_sum)

    keyboard = reply_keyboards.get_main_keyboard(show_reg_button=not user.is_reg, is_courier=user.courier)
    await message.answer('Изменено успешно!', reply_markup=keyboard)
    await state.finish()


async def add_courier_menu(call: CallbackQuery):
    db_session = call.bot.get('database')
    async with db_session() as session:
        records = await session.execute(select(Referral).where(Referral.is_original == True))
        referrals = records.scalars().all()

    await call.message.edit_text('Добавить курьера',
                                 reply_markup=inline_keyboards.get_choose_original_referral_keyboard(referrals))
    await call.answer()


async def choose_original_referral(call: CallbackQuery, callback_data: dict):
    original_ref_id = int(callback_data['original_ref_id'])
    page = int(callback_data['page'])

    async_session: AsyncSession = call.bot.get('database')
    config = call.bot.get('config')

    async with async_session.begin() as session:
        ref_ids = (await session.execute(select(Referral).where(Referral.original_referral_id == original_ref_id,
                                                                Referral.is_original == False))).all()
        ref_data = []
        for ref_id in ref_ids:
            referral = ref_id[0]

            user = await session.get(User, referral.telegram_id)

            ref_data.append(
                {'message': f'{user.name} - обменов в сумме {referral.deals_count + referral.ref_deals_count}',
                 'id': referral.id})
    await call.message.edit_text('Рефералы', reply_markup=inline_keyboards.get_referrals_list_keyboard(ref_data,
                                                                                                       config.misc.items_per_page,
                                                                                                       page,
                                                                                                       original_ref_id))
    await call.answer()


async def show_ref_account(call: CallbackQuery, callback_data: dict):
    original_ref_id = int(callback_data['original_ref_id'])
    page = int(callback_data['page'])
    ref_id = int(callback_data['ref_id'])
    async_session: AsyncSession = call.bot.get('database')

    async with async_session.begin() as session:
        referral = await session.get(Referral, ref_id)
        user = await session.get(User, referral.telegram_id)
        courier = await session.get(Courier, referral.telegram_id)
        if courier and not courier.deleted:
            will_be_courier = False
        else:
            will_be_courier = True
    await call.message.edit_text(
        messages.referral_info.format(
            telegram_id=referral.telegram_id,
            name=user.name,
            level=referral.level,
            deals_count=referral.deals_count,
            ref_deals_count=referral.ref_deals_count,
            email=user.email if user.email else 'Нет email',
            phone=user.phone if user.phone else 'Нет телефона'
        ),
        reply_markup=inline_keyboards.get_ref_account_keyboard('ref_list', ref_id, original_ref_id, page,
                                                               will_be_courier, referral.telegram_id)
    )
    await call.answer()


async def update_courier(call: CallbackQuery, callback_data: dict):
    telegram_id = int(callback_data['ref_id'])
    async_session: AsyncSession = call.bot.get('database')

    async with async_session.begin() as session:
        courier = await session.get(Courier, telegram_id)
        if courier and not courier.deleted:
            courier.deleted = True
            await call.answer('Курьер успешно удален', show_alert=True)
        elif courier and courier.deleted:
            courier.deleted = False
            await call.answer('Курьер успешно назначен', show_alert=True)
        else:
            courier = Courier(telegram_id=telegram_id)
            session.add(courier)

            await call.answer('Курьер успешно назначен', show_alert=True)

        records = await session.execute(select(Referral).where(Referral.is_original == True))
        referrals = records.scalars().all()

    await call.message.edit_text('Добавить курьера',
                                 reply_markup=inline_keyboards.get_choose_original_referral_keyboard(referrals))


async def active_couriers(call: CallbackQuery, callback_data: dict):
    page = int(callback_data['page'])
    async_session: AsyncSession = call.bot.get('database')
    config = call.bot.get('config')

    async with async_session.begin() as session:
        # couriers = (await session.execute(select(Courier).where(not Courier.deleted))).all()
        records = await session.execute(select(Courier).where(Courier.deleted == False, Courier.telegram_id > 3))
        couriers = records.scalars().all()
        to_menu = []
        for courier in couriers:
            user = await session.get(User, courier.telegram_id)
            to_menu.append({'name': user.name, 'telegram_id': courier.telegram_id})
    await call.message.edit_text('Активные сотрудники', reply_markup=inline_keyboards.get_active_couriers_list(to_menu,
                                                                                                               config.misc.items_per_page,
                                                                                                               page))
    await call.answer()


async def active_courier_info(call: CallbackQuery, callback_data: dict):
    telegram_id = int(callback_data['telegram_id'])
    page = int(callback_data['page'])

    async_session: AsyncSession = call.bot.get('database')
    config = call.bot.get('config')

    is_admin = telegram_id in config.tg_bot.admin_ids

    async with async_session.begin() as session:
        courier = await session.get(Courier, telegram_id)
        user = await session.get(User, telegram_id)
        referral = (await session.execute(select(Referral).where(Referral.telegram_id == telegram_id))).first()[0]
        days_from_reg = (datetime.datetime.now() - courier.created_at).days

    withdrawal_amount = courier.earned - courier.paid

    await call.message.edit_text(messages.active_courier_info.format(
        telegram_id=telegram_id,
        name=user.name,
        canceled_deals_count=courier.canceled_orders_count,
        weeks_live=days_from_reg // 7,
        created_at=courier.created_at,
        earned=courier.earned,
        level=referral.level,
        deals_count=referral.deals_count,
        ref_deals_count=referral.ref_deals_count,
        email=user.email if user.email else 'Нет email',
        phone=user.phone if user.phone else 'Нет телефона'
    ), reply_markup=inline_keyboards.get_active_courier_info_keyboard(is_admin, withdrawal_amount, page, telegram_id))
    await call.answer()


async def show_active_courier_withdrawal_history(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    telegram_id = int(callback_data['telegram_id'])
    page = callback_data['page']

    async with async_session.begin() as session:
        rub_thb_count = len((await session.execute(select(Order).where(Order.finished, Order.deal_type == DealType.CASH,
                                                                       Order.exchange_type == ExchangeType.RUB_THB,
                                                                       Order.courier_telegram_id == telegram_id))).all())
        thb_rub_count = len((await session.execute(select(Order).where(Order.finished, Order.deal_type == DealType.CASH,
                                                                       Order.exchange_type == ExchangeType.THB_RUB,
                                                                       Order.courier_telegram_id == telegram_id))).all())
        thb_usdt_count = len((await session.execute(
            select(Order).where(Order.finished, Order.deal_type == DealType.CASH,
                                Order.exchange_type == ExchangeType.THB_USDT,
                                Order.courier_telegram_id == telegram_id))).all())
        usdt_thb_count = len((await session.execute(
            select(Order).where(Order.finished == True, Order.deal_type == DealType.CASH,
                                Order.exchange_type == ExchangeType.USDT_THB,
                                Order.courier_telegram_id == telegram_id))).all())

    deal_count_info = [rub_thb_count, thb_rub_count, thb_usdt_count, usdt_thb_count]
    await call.message.edit_text('История заявок',
                                 reply_markup=inline_keyboards.get_courier_withdrawal_stat_list_keyboard(
                                     deal_count_info, telegram_id))
    await call.answer()


async def show_courier_deals_list_rub_thb(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    config = call.bot.get('config')
    telegram_id = int(callback_data['telegram_id'])
    page = int(callback_data['page'])

    async with async_session.begin() as session:
        deals = (await session.execute(
            select(Order).where(Order.exchange_type == ExchangeType.RUB_THB, Order.deal_type == DealType.CASH,
                                Order.courier_telegram_id == telegram_id))).all()
    if deals:
        deal = deals[page - 1][0]
        currency1, currency2 = deal.exchange_type.split('/')

        await call.message.edit_text(messages.order.format(
            bitrix_id=deal.bitrix_id,
            exchange_type=deal.exchange_type,
            username=deal.customer_name,
            customer_telegram_id=deal.customer_telegram_id,
            phone_number=deal.phone_number,
            receive_cur=currency2,
            customer_receive=deal.customer_receive,
            give_cur=currency1,
            customer_give=deal.customer_give,
            exchange_rate=deal.exchange_rate,
            location=deal.location,
            started_at=deal.started_at
        ), reply_markup=inline_keyboards.get_courier_deal_list(len(deals), page, telegram_id, 'rub/thb'))
        await call.answer()
    else:
        await call.answer('Нет выполненных заказов', show_alert=True)


async def show_courier_deals_list_thb_rub(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    config = call.bot.get('config')
    telegram_id = int(callback_data['telegram_id'])
    page = int(callback_data['page'])

    async with async_session.begin() as session:
        deals = (await session.execute(
            select(Order).where(Order.exchange_type == ExchangeType.THB_RUB, Order.deal_type == DealType.CASH,
                                Order.courier_telegram_id == telegram_id))).all()
    if deals:
        deal = deals[page - 1][0]
        currency1, currency2 = deal.exchange_type.split('/')

        await call.message.edit_text(messages.order.format(
            bitrix_id=deal.bitrix_id,
            exchange_type=deal.exchange_type,
            username=deal.customer_name,
            customer_telegram_id=deal.customer_telegram_id,
            phone_number=deal.phone_number,
            receive_cur=currency2,
            customer_receive=deal.customer_receive,
            give_cur=currency1,
            customer_give=deal.customer_give,
            exchange_rate=deal.exchange_rate,
            location=deal.location,
            started_at=deal.started_at
        ), reply_markup=inline_keyboards.get_courier_deal_list(len(deals), page, telegram_id, 'thb/rub'))
        await call.answer()
    else:
        await call.answer('Нет выполненных заказов', show_alert=True)


async def show_courier_deals_list_thb_usdt(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    config = call.bot.get('config')
    telegram_id = int(callback_data['telegram_id'])
    page = int(callback_data['page'])

    async with async_session.begin() as session:
        deals = (await session.execute(
            select(Order).where(Order.exchange_type == ExchangeType.THB_USDT, Order.deal_type == DealType.CASH,
                                Order.courier_telegram_id == telegram_id))).all()
    if deals:
        deal = deals[page - 1][0]
        currency1, currency2 = deal.exchange_type.split('/')

        await call.message.edit_text(messages.order.format(
            bitrix_id=deal.bitrix_id,
            exchange_type=deal.exchange_type,
            username=deal.customer_name,
            customer_telegram_id=deal.customer_telegram_id,
            phone_number=deal.phone_number,
            receive_cur=currency2,
            customer_receive=deal.customer_receive,
            give_cur=currency1,
            customer_give=deal.customer_give,
            exchange_rate=deal.exchange_rate,
            location=deal.location,
            started_at=deal.started_at
        ), reply_markup=inline_keyboards.get_courier_deal_list(len(deals), page, telegram_id, 'thb/usdt'))
        await call.answer()
    else:
        await call.answer('Нет выполненных заказов', show_alert=True)


async def show_courier_deals_list_usdt_thb(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    config = call.bot.get('config')
    telegram_id = int(callback_data['telegram_id'])
    page = int(callback_data['page'])

    async with async_session.begin() as session:
        deals = (await session.execute(
            select(Order).where(Order.exchange_type == ExchangeType.USDT_THB, Order.deal_type == DealType.CASH,
                                Order.courier_telegram_id == telegram_id))).all()
    if deals:
        deal = deals[page - 1][0]
        currency1, currency2 = deal.exchange_type.split('/')

        await call.message.edit_text(messages.order.format(
            bitrix_id=deal.bitrix_id,
            exchange_type=deal.exchange_type,
            username=deal.customer_name,
            customer_telegram_id=deal.customer_telegram_id,
            phone_number=deal.phone_number,
            receive_cur=currency2,
            customer_receive=deal.customer_receive,
            give_cur=currency1,
            customer_give=deal.customer_give,
            exchange_rate=deal.exchange_rate,
            location=deal.location,
            started_at=deal.started_at
        ), reply_markup=inline_keyboards.get_courier_deal_list(len(deals), page, telegram_id, 'usdt/thb'))
        await call.answer()
    else:
        await call.answer('Нет выполненных заказов', show_alert=True)


async def show_withdrawal_active_courier_menu(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    config = call.bot.get('config')
    telegram_id = int(callback_data['telegram_id'])
    page = int(callback_data['page'])

    async with async_session.begin() as session:
        week_data = (await session.execute(select(Statistic).where(Statistic.courier_id == telegram_id))).all()

    withdrawal_data = []
    for week in week_data:
        week = week[0]
        week_number = int(week.week_created_at.strftime("%V"))
        year = int(week.week_created_at.strftime("%Y"))
        message = f"Неделя {week_number} ({year}) - {'ВЫПЛАЧЕНО' if week.operator_status else 'НЕ ВЫПЛАЧЕНО'}"
        withdrawal_data.append({'message': message, 'stat_id': week.id})

    await call.message.edit_text(f'Выплаты(Страница {page} из {len(withdrawal_data)})',
                                 reply_markup=inline_keyboards.get_active_courier_withdrawal(withdrawal_data,
                                                                                             config.misc.items_per_page,
                                                                                             page, telegram_id))
    await call.answer()


async def show_active_courier_week_info(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    telegram_id = int(callback_data['telegram_id'])
    stat_id = int(callback_data['page'])

    async with async_session.begin() as session:
        week = await session.get(Statistic, stat_id)

    message = get_courier_stat_message(week)

    await call.message.edit_text(message,
                                 reply_markup=inline_keyboards.get_courier_week_statistic_for_operator(stat_id,
                                                                                                       week.operator_status,
                                                                                                       telegram_id))
    await call.answer()


async def get_courier_paid(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    telegram_id = int(callback_data['telegram_id'])
    stat_id = int(callback_data['page'])

    async with async_session.begin() as session:
        week = await session.get(Statistic, stat_id)
        week.operator_status = True

    message = get_courier_stat_message(week)

    await call.message.edit_text(message,
                                 reply_markup=inline_keyboards.get_courier_week_statistic_for_operator(stat_id,
                                                                                                       week.operator_status,
                                                                                                       telegram_id))
    await call.answer()


async def send_operator_menu(message: Message):
    db_session = message.bot.get('database')
    async with db_session() as session:
        user = await session.get(User, message.from_id)
        if not user.operator:
            await message.answer('Вы не оператор')
            return

    await message.answer('Меню оператора', reply_markup=inline_keyboards.operator_menu)


async def show_operator_menu(call: CallbackQuery):
    await call.message.edit_text('Меню оператора', reply_markup=inline_keyboards.operator_menu)
    await call.answer()


async def check_order(call: CallbackQuery, callback_data: dict):
    order_id = int(callback_data['order_id'])
    db_session = call.bot.get('database')
    async with db_session() as session:
        order = await session.get(Order, order_id)

    if order.operator:
        await call.answer('Заказ уже обрабатывает другой оператор!', show_alert=True)
    else:
        await call.answer('Заказ никто не обрабатывает!', show_alert=True)


async def take_order(call: CallbackQuery, callback_data: dict):
    order_id = int(callback_data['order_id'])
    db_session = call.bot.get('database')
    async with db_session.begin() as session:
        order = await session.get(Order, order_id)
        if await is_canceled(call.message, order.bitrix_id):
            return

        if order.operator:
            await call.answer('Заказ уже обрабатывает другой оператор!', show_alert=True)
            return

        order.operator_id = call.from_user.id
        order.answered_at = datetime.datetime.now()
        await call.answer('Вы назначены на этот заказ!', show_alert=True)
    # if order.exchange_type in (ExchangeType.THB_USDT, ExchangeType.THB_RUB):
    if order.deal_type == DealType.CASH or order.deal_type == DealType.COURIER:
        # todo: send courier choose menu here
        async with db_session() as session:
            available_couriers = (await session.execute(select(Courier).where(Courier.is_free == True))).scalars().all()
            available_couriers = [{'name': i.user.username, 'telegram_id': i.telegram_id} for i in available_couriers]

        await call.message.edit_text('Свободные курьеры', reply_markup=inline_keyboards.get_couriers_choose(available_couriers, order_id))
        await call.answer()
        return

    await call.bot.send_message(
        order.customer_telegram_id,
        messages.update_rate_input,
        reply_markup=inline_keyboards.get_notify_keyboard(order_id)
    )

    await call.message.edit_text('Ждем пока клиент обновит курс')
    await call.answer()


async def get_courier_choose(call: CallbackQuery, callback_data: dict):
    telegram_id = int(callback_data['telegram_id'])
    order_id = int(callback_data['order_id'])
    db_session = call.bot.get('database')
    async with db_session.begin() as session:
        order = await session.get(Order, order_id)
        courier = await session.get(Courier, telegram_id)
        if await is_canceled(call.message, order.bitrix_id):
            return
        if not courier.is_free:
            await call.answer('Курьер занят')
            await take_order(call, {'order_id': order_id})
            return
        courier.is_free = False
        order.courier_telegram_id = telegram_id
        await call.message.edit_text('Курьер успешно назначен')

        await call.bot.send_message(
            chat_id=telegram_id,
            text=messages.get_courier_delivery_message(order, order.customer.username),
            reply_markup=inline_keyboards.get_courier_on_the_way_keyboard(order.bitrix_id)
        )
        await call.answer()


async def get_update_rate_from_user(call: CallbackQuery, callback_data: dict, state: FSMContext):
    order_id = int(callback_data['deal_id'])
    db_session = call.bot.get('database')
    async with db_session.begin() as session:
        order = await session.get(Order, order_id)
        if await is_canceled(call.message, order.bitrix_id):
            return
    await states.OperatorOrderState.waiting_for_requisites.set()
    await state.update_data(order_id=order_id, customer_telegram_id=order.customer_telegram_id)
    await call.message.edit_text('Введите реквизиты:')
    await call.answer()


async def get_requisites(message: Message, state: FSMContext):
    requisites = message.text

    state_data = await state.get_data()
    await message.bot.send_message(
        chat_id=state_data['customer_telegram_id'],
        text=f'Реквизиты для перевода:\n{md.hcode(requisites)}\nПосле перевода прикрепите скан.',
        reply_markup=inline_keyboards.get_customer_order_keyboard(int(state_data['order_id']))
    )
    await message.answer('Ожидаем ответ от пользователя!')
    await state.finish()


async def confirm_order(call: CallbackQuery, callback_data: dict):
    db_session = call.bot.get('database')
    async with db_session.begin() as session:
        order = await session.get(Order, int(callback_data['order_id']))
        order.confirmed_at = datetime.datetime.now()
    if order.courier_telegram_id:
        text_for_courier = messages.courier_text.format(
            username=order.customer_name,
            phone=order.phone_number,
            location=order.location,
            comment=order.location_comment,
            deal_type=order.deal_type,
            give=order.customer_give,
            receive=order.customer_receive,
        )

        await call.bot.send_message(
            chat_id=order.courier_telegram_id,
            text=text_for_courier,
            reply_markup=inline_keyboards.get_delivery_confirm_keyboard(order.bitrix_id)
        )
    else:
        await call.bot.send_message(
            chat_id=order.customer_telegram_id,
            text='Ваш заказ обработан!\nПожалуйста, подтвердите получение средств',
            reply_markup=inline_keyboards.get_receive_confirm_keyboard(order.bitrix_id)
        )

    await call.message.edit_reply_markup()
    await call.answer('Заказ подтвержден!', show_alert=True)


async def show_active_orders_list(call: CallbackQuery):
    async_session: AsyncSession = call.bot.get('database')
    async with async_session.begin() as session:
        orders = (await session.execute(select(Order).where(Order.finished == False, Order.is_canceled == False))).all()
    await call.message.edit_text('Текущие заказы', reply_markup=inline_keyboards.get_active_orders_list(orders))
    await call.answer()


async def show_active_order_info(call: CallbackQuery, callback_data: dict):
    order_id = int(callback_data['payload'])
    async_session: AsyncSession = call.bot.get('database')
    async with async_session.begin() as session:
        order = await session.get(Order, order_id)
    currency1, currency2 = order.exchange_type.split('/')
    message_data = [currency1, order.customer_give, currency2, order.customer_receive, order.exchange_rate,
                    order.phone_number, order.customer_name, order.bitrix_id, order.customer.username]
    custom_data = get_custom_fields(order)

    msg = messages.get_message_from_crm(order.exchange_type, order.deal_type, message_data, custom_data)
    await call.message.edit_text(msg, reply_markup=inline_keyboards.get_cancel_order_menu(order_id))
    await call.answer()


async def cancel_active_order(call: CallbackQuery, callback_data: dict):
    order_id = int(callback_data['payload'])
    async_session: AsyncSession = call.bot.get('database')
    async with async_session.begin() as session:
        order = await session.get(Order, order_id)
        courier_telegram_id = order.courier_telegram_id
        operator_telegram_id = order.operator_id
        customer_telegram_id = order.customer_telegram_id
        courier = await session.get(Courier, courier_telegram_id)
        courier_user = await session.get(User, courier_telegram_id)
        await session.execute(
            update(Order).where(Order.bitrix_id == order_id).values(is_canceled=True, courier_telegram_id=None,
                                                                    operator_id=None))
    currency1, currency2 = order.exchange_type.split('/')
    message_data = [currency1, order.customer_give, currency2, order.customer_receive, order.exchange_rate,
                    order.phone_number, order.customer_name, order.bitrix_id, order.customer.username]
    custom_data = get_custom_fields(order)

    msg = messages.get_message_from_crm(order.exchange_type, order.deal_type, message_data, custom_data)
    # todo: send to operator that order is canceled
    if courier_telegram_id:
        # todo: make courier available
        await call.bot.send_message(courier_telegram_id, 'Отмена заявки\n\n' + msg)
    if operator_telegram_id:
        await call.bot.send_message(operator_telegram_id, 'Отмена заявки\n\n' + msg)
    await call.bot.send_message(customer_telegram_id,
                                'По техническим причинам Ваша заявка отменена. Пожалуйста оформите новую заявку')

    async with async_session.begin() as session:
        orders = (await session.execute(select(Order).where(Order.finished == False, Order.is_canceled == False))).all()
    await call.message.edit_text('Текущие заказы', reply_markup=inline_keyboards.get_active_orders_list(orders))
    await call.answer('Заказ отменен', show_alert=True)


def register_operator(dp: Dispatcher):
    dp.register_message_handler(send_operator_menu, commands=['operator'])
    dp.register_callback_query_handler(show_operator_menu, callbacks.navigation.filter(to='operator_menu'))
    dp.register_callback_query_handler(show_operator_order_list, callbacks.navigation.filter(to='order_list'))
    dp.register_callback_query_handler(courier_change_menu, callbacks.navigation.filter(to='courier_change_menu'))
    dp.register_message_handler(send_courier_change_menu, text=reply_commands.courier_change_menu)
    dp.register_message_handler(send_operator_order_list, text=reply_commands.operator_order_list)
    dp.register_callback_query_handler(show_years_choose, callbacks.navigation.filter(to='years'))
    dp.register_callback_query_handler(show_weeks, callbacks.year_choose.filter())
    dp.register_callback_query_handler(show_days, callbacks.week_choose.filter(action='oper'))
    dp.register_callback_query_handler(show_orders, callbacks.day_choose.filter())
    dp.register_callback_query_handler(show_order, callbacks.order_choose.filter())
    dp.register_callback_query_handler(start_sum_input, callbacks.order_update.filter())
    dp.register_message_handler(get_sum, state=states.OrderUpdateState.waiting_for_value)
    dp.register_callback_query_handler(add_courier_menu, callbacks.navigation.filter(to='add_courier'))
    dp.register_callback_query_handler(choose_original_referral, callbacks.referral_list.filter(to='ref_list'))
    dp.register_callback_query_handler(show_ref_account, callbacks.referral_list.filter(to='ref_account'))
    dp.register_callback_query_handler(update_courier, callbacks.referral_list.filter(to='update_courier'))
    dp.register_callback_query_handler(active_couriers, callbacks.active_couriers.filter(to='active_couriers'))
    dp.register_callback_query_handler(active_courier_info, callbacks.active_couriers.filter(to='courier'))
    dp.register_callback_query_handler(show_active_courier_withdrawal_history,
                                       callbacks.active_couriers.filter(to='withdrawal_history'))
    dp.register_callback_query_handler(show_courier_deals_list_rub_thb, callbacks.active_couriers.filter(to='rub/thb'))
    dp.register_callback_query_handler(show_courier_deals_list_thb_rub, callbacks.active_couriers.filter(to='thb/rub'))
    dp.register_callback_query_handler(show_courier_deals_list_thb_usdt,
                                       callbacks.active_couriers.filter(to='thb/usdt'))
    dp.register_callback_query_handler(show_courier_deals_list_usdt_thb,
                                       callbacks.active_couriers.filter(to='usdt/thb'))
    dp.register_callback_query_handler(show_withdrawal_active_courier_menu,
                                       callbacks.active_couriers.filter(to='withdrawal'))
    dp.register_callback_query_handler(show_active_courier_week_info, callbacks.active_couriers.filter(to='week_info'))
    dp.register_callback_query_handler(get_courier_paid, callbacks.active_couriers.filter(to='courier_paid'))

    dp.register_callback_query_handler(check_order, callbacks.operator_order.filter(action='check'))
    dp.register_callback_query_handler(take_order, callbacks.operator_order.filter(action='take'))
    dp.register_message_handler(get_requisites, state=states.OperatorOrderState.waiting_for_requisites)
    dp.register_callback_query_handler(confirm_order, callbacks.operator_order.filter(action='confirm'))
    dp.register_callback_query_handler(show_active_orders_list, callbacks.navigation.filter(to='active_orders'))
    dp.register_callback_query_handler(show_active_order_info, callbacks.navigation.filter(to='active_order_info'))
    dp.register_callback_query_handler(cancel_active_order, callbacks.navigation.filter(to='cancel_order'))
    dp.register_callback_query_handler(get_update_rate_from_user, callbacks.crm_notify.filter(payload='confirm_update'))
    dp.register_callback_query_handler(get_courier_choose, callbacks.courier_choose.filter())
