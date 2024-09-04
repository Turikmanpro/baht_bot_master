import datetime

from aiogram import Dispatcher
from aiogram.types import CallbackQuery, Message
from aiogram_broadcaster import TextBroadcaster
from fast_bitrix24 import BitrixAsync
from sqlalchemy import update

import tgbot.keyboards.inline as inline_keyboards
import tgbot.misc.callbacks as callbacks
from tgbot.config import Config
from tgbot.misc import reply_commands
from tgbot.misc.helper import *
import tgbot.misc.messages as messages
from tgbot.services.bitrix.bitrix import change_deal_stage, change_courier_availability
from tgbot.services.bitrix.bitrix_schemas import SellStage
from tgbot.services.bitrix.get_deals import get_deal
from tgbot.services.database.models import Courier, Statistic, User


async def courier_deliveries(call: CallbackQuery):
    async_session: AsyncSession = call.bot.get('database')

    async with async_session.begin() as session:
        stm = f'select bitrix_id from bitrix_order where courier_telegram_id = {call.from_user.id} and not finished'
        order_id = (await session.execute(stm)).first()

    if order_id:
        async with async_session.begin() as session:
            order = await session.get(Order, int(order_id))

        message = messages.get_courier_delivery_message(order, order.customer.username)
        await call.message.edit_text(message,
                                     reply_markup=inline_keyboards.get_courier_arrived_keyboard(order_id))
    else:
        await call.message.edit_text('Нет доступных доставок')

    await call.answer()


async def send_courier_deliveries(message: Message):
    async_session: AsyncSession = message.bot.get('database')

    async with async_session.begin() as session:
        stm = f'select bitrix_id from bitrix_order where courier_telegram_id = {message.from_user.id} and not finished'
        order_id = (await session.execute(stm)).first()

    if order_id:
        async with async_session.begin() as session:
            order = await session.get(Order, int(order_id))

        message_text = messages.get_courier_delivery_message(order, order.customer.username)
        await message.answer(message_text,
                             reply_markup=inline_keyboards.get_courier_arrived_keyboard(order_id))
    else:
        await message.answer('Нет доступных доставок')


async def courier_on_the_way(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    order_id = int(callback_data['order_id'])

    async with async_session.begin() as session:
        order = await session.get(Order, int(order_id))
        if await is_canceled(call.message, order.bitrix_id, 'Заказ был отменен оператором'):
            return

    await call.bot.send_message(
        order.operator_id,
        'courier is on the way'
    )

    message_text = messages.get_courier_delivery_message(order, order.customer.username)
    await call.message.edit_text(message_text,
                                 reply_markup=inline_keyboards.get_courier_arrived_keyboard(order_id))
    await call.answer()


async def courier_arrived(call: CallbackQuery, callback_data: dict):
    # move to exchange stage in bitrix
    async_session: AsyncSession = call.bot.get('database')
    order_id = int(callback_data['order_id'])

    async with async_session.begin() as session:
        order = await session.get(Order, int(order_id))
        if await is_canceled(call.message, order.bitrix_id, 'Заказ был отменен оператором'):
            return

    message = messages.get_courier_delivery_message(order, order.customer.username)
    # todo: send to operator that courier is arrived
    await call.message.edit_text('ВНИМАНИЕ! ЖДИТЕ СООБЩЕНИЕ ОТ ОПЕРАТОРА О ВЫДАЧЕ\n\n' + message)

    # send order message to customer
    await call.bot.send_message(
        order.customer_telegram_id, messages.update_rate_input, reply_markup=inline_keyboards.get_notify_keyboard(order_id)
    )
    await call.answer()


async def courier_account(call: CallbackQuery):
    async_session: AsyncSession = call.bot.get('database')

    async with async_session.begin() as session:
        order_ids = (await session.execute(
            select(Order).where(Order.courier_telegram_id == call.from_user.id, Order.finished))).all()
        courier_data = await session.get(Courier, call.from_user.id)

    finished_orders = len(order_ids)
    days_from_reg = (datetime.datetime.now() - courier_data.created_at).days

    msg = messages.courier_account.format(
        finished_orders=finished_orders,
        canceled_orders_count=courier_data.canceled_orders_count,
        days_from_reg=days_from_reg // 7,
        created_at=courier_data.created_at.strftime('%d %b %Y'),
        earned=courier_data.earned
    )

    button_message = courier_data.earned - courier_data.paid

    await call.message.edit_text(msg, reply_markup=inline_keyboards.get_courier_account_keyboard(button_message))
    await call.answer()


async def send_courier_account(message: Message):
    async_session: AsyncSession = message.bot.get('database')

    async with async_session.begin() as session:
        order_ids = (await session.execute(
            select(Order).where(Order.courier_telegram_id == message.from_user.id, Order.finished))).all()
        courier_data = await session.get(Courier, message.from_user.id)

    finished_orders = len(order_ids)
    days_from_reg = (datetime.datetime.now() - courier_data.created_at).days
    msg = messages.courier_account.format(
        finished_orders=finished_orders,
        canceled_orders_count=courier_data.canceled_orders_count,
        days_from_reg=days_from_reg // 7,
        created_at=courier_data.created_at.strftime('%d %b %Y'),
        earned=courier_data.earned
    )

    button_message = courier_data.earned - courier_data.paid

    await message.answer(msg, reply_markup=inline_keyboards.get_courier_account_keyboard(button_message))


async def courier_withdrawal_history(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    config: Config = call.bot.get('config')

    async with async_session.begin() as session:
        week_data = (await session.execute(select(Statistic).where(Statistic.courier_id == call.from_user.id))).all()

    withdrawal_data = []
    for week in week_data:
        week = week[0]
        week_number = int(week.week_created_at.strftime("%V"))
        year = int(week.week_created_at.strftime("%Y"))
        message = f"Неделя {week_number} ({year}) - {'ВЫПЛАЧЕНО' if week.operator_status else 'НЕ ВЫПЛАЧЕНО'}"
        withdrawal_data.append({'message': message, 'stat_id': week.id})

    await call.message.edit_text(f'История заявок(Страница {callback_data["payload"]} из {len(withdrawal_data)})',
                                 reply_markup=inline_keyboards.get_withdrawal_history(withdrawal_data,
                                                                                      config.misc.items_per_page,
                                                                                      int(callback_data[
                                                                                              'payload'])))
    await call.answer()


def get_courier_stat_message(week):
    week_number = int(week.week_created_at.strftime("%V"))
    year = int(week.week_created_at.strftime("%Y"))
    message = f'''
Неделя - {week_number} ({year})
Выполнено заказов - {week.completed_orders}
Отменено заказов - {week.canceled_orders}
Заработано - {week.courier_earned} USDT
Статус оператор - {'ВЫПЛАЧЕНО' if week.operator_status else 'НЕ ВЫПЛАЧЕНО'}
Статус курьер - {'ПОЛУЧИЛ' if week.courier_status else 'ОЖИДАНИЕ'}
                   '''
    return message


async def courier_week_statistic(call: CallbackQuery, callback_data: dict):
    stat_id = int(callback_data['stat_id'])
    async_session: AsyncSession = call.bot.get('database')

    async with async_session.begin() as session:
        week = await session.get(Statistic, stat_id)

    message = get_courier_stat_message(week)
    await call.message.edit_text(message,
                                 reply_markup=inline_keyboards.get_courier_week_statistic(stat_id, week.courier_status))
    await call.answer()


async def courier_received(call: CallbackQuery, callback_data: dict):
    stat_id = int(callback_data['payload'])
    async_session: AsyncSession = call.bot.get('database')

    async with async_session.begin() as session:
        await session.execute(update(Statistic).where(Statistic.id == stat_id).values(courier_status=True))
        week = await session.get(Statistic, stat_id)

    message = get_courier_stat_message(week)
    await call.message.edit_text(message, reply_markup=inline_keyboards.get_courier_week_statistic(stat_id,
                                                                                                   week.courier_status))
    await call.answer()


async def send_courier_menu(message: Message):
    db_session = message.bot.get('database')
    async with db_session() as session:
        user = await session.get(User, message.from_id)
        if not user.courier:
            await message.answer('Вы не курьер')
            return

    await message.answer('Меню курьера', reply_markup=inline_keyboards.courier_menu)


async def show_courier_menu(call: CallbackQuery):
    await call.message.edit_text('Меню курьера', reply_markup=inline_keyboards.courier_menu)
    await call.answer()


async def confirm_delivery(call: CallbackQuery, callback_data: dict):
    db_session = call.bot.get('database')
    async with db_session.begin() as session:
        order = await session.get(Order, int(callback_data['order_id']))
        order.delivered_at = datetime.datetime.now()

    await call.message.edit_text(call.message.text)

    await call.bot.send_message(
        chat_id=order.customer_telegram_id,
        text='Ваш заказ доставлен!',
        reply_markup=inline_keyboards.get_receive_confirm_keyboard(order.bitrix_id)
    )

    await call.message.edit_reply_markup()
    await call.answer('Заказчику отправлено уведомление о доставке!', show_alert=True)


async def courier_cancel(call: CallbackQuery, callback_data: dict):
    order_id = int(callback_data['payload'])
    # change courier status
    async_session: AsyncSession = call.bot.get('database')

    async with async_session.begin() as session:
        await session.execute(update(Order).where(Order.bitrix_id == order_id).values(courier_telegram_id=None))
        await session.execute(update(Courier).where(Courier.telegram_id == call.from_user.id).values(canceled_orders_count=Courier.canceled_orders_count + 1))
        courier = await session.get(Courier, call.from_user.id)
        courier_user = await session.get(User, call.from_user.id)
        statement = f'select telegram_id from operator where deleted=false'
        operators_id = (await session.execute(statement)).scalars().all()

    # todo: set courier available
    # todo: send to operator that deal canceled

    await TextBroadcaster(
        chats=operators_id,
        text=f'Курьер отказался от доставки на заказе {order_id}. Назначьте нового курьера.'
    ).run()

    await call.message.edit_text('Вы отказались от доставки')
    await call.answer()


def register_courier(dp: Dispatcher):
    dp.register_message_handler(send_courier_menu, commands=['courier'])
    dp.register_callback_query_handler(show_courier_menu, callbacks.navigation.filter(to='courier_menu'))
    dp.register_callback_query_handler(courier_deliveries, callbacks.navigation.filter(to='courier_deliveries'))
    dp.register_message_handler(send_courier_deliveries, text=reply_commands.courier_deliveries)
    dp.register_callback_query_handler(courier_arrived, callbacks.courier.filter(payload='arrived'))
    dp.register_callback_query_handler(courier_account, callbacks.navigation.filter(to='courier_account'))
    dp.register_message_handler(send_courier_account, text=reply_commands.courier_account)
    dp.register_callback_query_handler(courier_withdrawal_history, callbacks.statistic.filter(action='courier_list'))
    dp.register_callback_query_handler(courier_week_statistic, callbacks.withdrawal_history.filter())
    dp.register_callback_query_handler(courier_received, callbacks.statistic.filter(action='courier_received'))
    dp.register_callback_query_handler(confirm_delivery, callbacks.courier_order.filter())
    dp.register_callback_query_handler(courier_on_the_way, callbacks.courier.filter(payload='on_the_way'))
    dp.register_callback_query_handler(courier_cancel, callbacks.navigation.filter(to='courier_cancel'))
