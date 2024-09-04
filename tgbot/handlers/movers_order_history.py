import datetime

from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import tgbot.keyboards.inline_permutations_keyboards as inline
from tgbot.handlers.admin import show_admin_menu
from tgbot.handlers.permutations_deal_calc import convert_to_full_names
from tgbot.misc import messages, callbacks
from tgbot.services.bitrix.bitrix_schemas import DealType
from tgbot.services.database.models import User, Referral, Mover, MoverOrder


async def show_active_orders(call: CallbackQuery):
    async_session: AsyncSession = call.bot.get('database')
    async with async_session.begin() as session:
        active_orders = (await session.execute(select(MoverOrder))).scalars().all()
        active_orders = [{'name': f'{i.exchange_type} {i.acceptance_city} {i.receive_place}', 'id': i.id} for i in active_orders]
    await call.message.edit_text('Заказы перестановки', reply_markup=inline.get_active_movers_order(active_orders))


async def show_mover_order(call: CallbackQuery, callback_data: dict):
    order_id = int(callback_data['order_id'])
    async_session: AsyncSession = call.bot.get('database')
    async with async_session.begin() as session:
        order = await session.get(MoverOrder, order_id)
        user = await session.get(User, order.customer_telegram_id)
    tz = datetime.timezone(datetime.timedelta(hours=7), "Thai")
    if order.deal_type == DealType.OFTEN_DEAL:
        country, receiving_office = order.receive_place.split('-')
        msg = messages.often_deal_mover_message.format(
            mover_order_id=order_id,
            date=datetime.datetime.now(tz=tz).strftime("%d.%m.%Y"),
            name=user.name,
            phone=user.phone,
            username=user.username,
            acceptance_city=convert_to_full_names(order.acceptance_city),
            country=f'{convert_to_full_names(country)} - {convert_to_full_names(receiving_office)}',
            currency='RUB',
            amount=order.customer_give,
            amount_2=order.customer_receive,
            ex_rate=order.exchange_rate
        )
    elif order.deal_type == DealType.QUICK_DEAL:
        msg = messages.quick_deal_mover_message.format(
            mover_order_id=order_id,
            date=datetime.datetime.now(tz=tz).strftime("%d.%m.%Y"),
            name=user.name,
            phone=user.phone,
            username=user.username,
            acceptance_city=order.acceptance_city,
            country=order.receive_place,
            currency=order.exchange_type.split('/')[0],
            amount=order.customer_give,
        )
    else:
        msg = 'Ошибка загрузки'
    await call.message.edit_text(msg, reply_markup=inline.back_to_mover_admin)
    await call.answer()


async def show_orders_history(call: CallbackQuery):
    async_session: AsyncSession = call.bot.get('database')


def register_movers_order_history(dp: Dispatcher):
    dp.register_callback_query_handler(show_active_orders, callbacks.movers.filter(to='orders_now'))
    dp.register_callback_query_handler(show_mover_order, callbacks.movers_order.filter(action='show'))
    # dp.register_callback_query_handler(show_orders_history, callbacks.movers.filter(to='order_history'))
