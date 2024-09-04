import datetime
from decimal import Decimal

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_broadcaster import TextBroadcaster
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import tgbot.keyboards.inline as inline_keyboards
import tgbot.misc.callbacks as callbacks
from tgbot.handlers.exchange import get_exchange_rate, get_amounts, get_custom_fields, get_ex_rate_with_percents
from tgbot.keyboards import reply_keyboards
from tgbot.keyboards.inline_keyboards import get_reviews_link_keyboard
from tgbot.keyboards.reply_keyboards import cancel
from tgbot.misc import messages, states
from tgbot.misc.helper import all_ref_stat, get_orig_earned_factor, get_rate
from tgbot.misc.messages import after_ex_rate_update
from tgbot.services.bitrix.bitrix_schemas import DealType, ExchangeType
from tgbot.services.database.models import Order, User, Courier, Statistic


async def finish_order(call: CallbackQuery, callback_data: dict):
    # finish deals
    async_session: AsyncSession = call.bot.get('database')

    deal_id = int(callback_data['deal_id'])
    # todo: send to operator that order finished

    async with async_session.begin() as session:
        order = await session.get(Order, deal_id)
        order.finished = True
        order.finished_at = datetime.datetime.now()
        stat_id = order.stat_week_id
        courier_earn = order.courier_earn

        user = await session.get(User, call.from_user.id)

        if courier_earn != 0:
            print(f'Cash deal {order.bitrix_id}')
            # add statistic to courier account
            statistic = await session.get(Statistic, stat_id)
            statistic.courier_earned += courier_earn
            statistic.completed_orders += 1

            courier_id = order.courier_telegram_id
            courier = await session.get(Courier, courier_id)
            courier.earned += courier_earn

            courier_user = await session.get(User, courier_id)
            # todo: set courier available

            await call.bot.send_message(
                order.courier_telegram_id,
                f'Сделка номер {order.bitrix_id} завершена. Ваш заработок - {courier_earn} USDT'
            )

        # append dividends to orig ref for week
        stat_week = (
            (await session.execute(select(Statistic).where(Statistic.courier_id == user.referral.original_referral_id,
                                                           Statistic.week_created_at - datetime.datetime.now() < datetime.timedelta(
                                                               days=7)))).first())
        if stat_week:
            stat_id = stat_week[0].id
            orig_statistic = await session.get(Statistic, stat_id)
            orig_statistic.courier_earned += float(await get_rate(order.customer_give,
                                                                  get_orig_earned_factor(user.referral.level),
                                                                  order.exchange_type))
        else:
            new_stat = Statistic(courier_id=user.referral.original_referral_id, courier_earned=(
                await get_rate(order.customer_give, get_orig_earned_factor(user.referral.level), order.exchange_type)))
            session.add(new_stat)

    await all_ref_stat(call.bot, async_session, order)

    # send final message to operator
    currency1, currency2 = order.exchange_type.split('/')
    message_data = [currency1, order.customer_give, currency2, order.customer_receive, order.exchange_rate,
                    order.phone_number, order.customer_name, order.bitrix_id, order.customer.username]
    custom_data = get_custom_fields(order)

    msg_text = messages.get_message_from_crm(order.exchange_type, order.deal_type, message_data, custom_data)
    await call.bot.send_message(
        order.operator_id,
        'Сделка завершена\n\n' + msg_text
    )

    await call.message.edit_text(
        ('Спасибо, что выбрали наш сервис!\n\n'

         'Рекомендуйте сервис Вашим друзьям и зарабатывайте дивиденды на их обменах.\n'
         'Узнайте подробности в разделе “Зарабатывай”'),
        reply_markup=get_reviews_link_keyboard('https://t.me/swapbotsupport')
    )
    keyboard = reply_keyboards.get_main_keyboard(show_reg_button=not user.is_reg, is_courier=user.courier)
    await call.message.answer(messages.main_menu, reply_markup=keyboard)


async def update_rate(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    config = call.bot.get('config')

    deal_id = int(callback_data['deal_id'])
    async with async_session.begin() as session:
        order = await session.get(Order, deal_id)
        deal_type = order.deal_type
        ex_type = order.exchange_type

        ex_rate = await get_exchange_rate(ex_type)
        ex_rate = get_ex_rate_with_percents(config, ex_rate, ex_type, deal_type)
        print('update_rate', ex_rate, ex_type, deal_type)

        currency1, currency2 = ex_type.split('/')
        input_currency = order.input_currency
        if input_currency == currency1:
            input_amount = Decimal(order.customer_give)
        else:
            input_amount = Decimal(order.customer_receive)
        customer_give, customer_receive = get_amounts(ex_type, input_currency, input_amount, ex_rate)

        if currency2 == 'THB':
            customer_receive = round(customer_receive / 100) * 100
        print('update_rate', ex_type, customer_give, customer_receive)

        order.exchange_rate = float(ex_rate)
        order.customer_give = customer_give
        order.customer_receive = customer_receive

    await call.message.edit_text('Вы можете изменить сумму заказа',
                                 reply_markup=inline_keyboards.get_client_change_order_sum(order.bitrix_id, currency1, currency2))
    await call.answer()


async def input_change_order_sum(call: CallbackQuery, callback_data: dict, state: FSMContext):
    order_id = int(callback_data['order_id'])
    input_currency = callback_data['input_currency']
    await call.message.delete()
    await call.message.answer(f'Введите новую сумму в {input_currency}', reply_markup=cancel)
    await states.ClientChange.waiting_for_sum.set()
    await state.update_data(order_id=order_id, input_currency=input_currency)
    await call.answer()


async def get_change_order_sum(message: Message, state: FSMContext):
    async_session: AsyncSession = message.bot.get('database')
    input_amount = Decimal(message.text)

    async with state.proxy() as data:
        order_id = int(data['order_id'])
        input_currency = data['input_currency']
    await state.finish()

    # send to all operators data about deal
    async with async_session.begin() as session:
        statement = f'select telegram_id from operator where deleted=false'
        operators_id = (await session.execute(statement)).scalars().all()

        order = await session.get(Order, order_id)

        ex_type = order.exchange_type
        deal_type = order.deal_type

        # get new give and receive sum
        ex_rate = Decimal(order.exchange_rate).quantize(Decimal('1.000'))

        currency1, currency2 = ex_type.split('/')
        customer_give, customer_receive = get_amounts(ex_type, input_currency, input_amount, ex_rate)
        if currency2 == 'THB':
            customer_receive = round(customer_receive / 100) * 100

        order.customer_give = customer_give
        order.customer_receive = customer_receive

    message_data = [currency1, order.customer_give, currency2, order.customer_receive, order.exchange_rate,
                    order.phone_number, order.customer_name, order.bitrix_id, order.customer.username]
    custom_data = get_custom_fields(order)

    msg = 'Уточнение курса\n\n' + messages.get_message_from_crm(ex_type, deal_type, message_data, custom_data)

    await message.bot.send_message(
        chat_id=order.operator_id,
        text=msg,
        reply_markup=inline_keyboards.get_input_requisites(order_id)
    )
    if order.exchange_type in (ExchangeType.THB_USDT, ExchangeType.THB_RUB):
        if order.deal_type == DealType.CASH:
            await message.answer('Ожидайте, оператор скоро одобрит сделку\n\n' + after_ex_rate_update.format(
                ex_rate=ex_rate,
                customer_give_currency=(order.exchange_type.split('/'))[0],
                customer_give=order.customer_give,
                customer_receive_currency=(order.exchange_type.split('/'))[1],
                customer_receive=order.customer_receive
            ))
            return

    # send to client new give adn receive sum
    await message.answer(
        'ВНИМАНИЕ! Ожидайте сообщения от оператора с реквизитами для перевода\n\n' + after_ex_rate_update.format(
            ex_rate=ex_rate,
            customer_give_currency=(order.exchange_type.split('/'))[0],
            customer_give=order.customer_give,
            customer_receive_currency=(order.exchange_type.split('/'))[1],
            customer_receive=order.customer_receive
        ))


async def get_no_change_order_sum(call: CallbackQuery, callback_data: dict):
    order_id = int(callback_data['order_id'])

    db_session = call.bot.get('database')
    async with db_session() as session:
        statement = f'select telegram_id from operator where deleted=false'
        operators_id = (await session.execute(statement)).scalars().all()

        order = await session.get(Order, order_id)

        ex_type = order.exchange_type
        deal_type = order.deal_type

    currency1, currency2 = order.exchange_type.split('/')
    message_data = [currency1, order.customer_give, currency2, order.customer_receive, order.exchange_rate,
                    order.phone_number, order.customer_name, order.bitrix_id, order.customer.username]
    custom_data = get_custom_fields(order)

    msg = 'Уточнение курса\n\n' + messages.get_message_from_crm(ex_type, deal_type, message_data, custom_data)

    await call.bot.send_message(
        chat_id=order.operator_id,
        text=msg,
        reply_markup=inline_keyboards.get_input_requisites(order_id)
    )
    if order.exchange_type in (ExchangeType.THB_USDT, ExchangeType.THB_RUB):
        if order.deal_type == DealType.CASH:
            await call.message.answer('Ожидайте, оператор скоро одобрит сделку\n\n' + after_ex_rate_update.format(
                ex_rate=order.exchange_rate,
                customer_give_currency=(order.exchange_type.split('/'))[0],
                customer_give=order.customer_give,
                customer_receive_currency=(order.exchange_type.split('/'))[1],
                customer_receive=order.customer_receive
            ))
            await call.answer()
            return
    await call.message.answer('Ожидайте сообщения от оператора с реквизитами для перевода\n\n' + after_ex_rate_update.format(
                ex_rate=order.exchange_rate,
                customer_give_currency=(order.exchange_type.split('/'))[0],
                customer_give=order.customer_give,
                customer_receive_currency=(order.exchange_type.split('/'))[1],
                customer_receive=order.customer_receive
            ))
    await call.answer()


def register_notify(dp: Dispatcher):
    dp.register_callback_query_handler(finish_order, callbacks.crm_notify.filter(payload='ok'))
    dp.register_callback_query_handler(update_rate, callbacks.crm_notify.filter(payload='update_rate'))
    dp.register_callback_query_handler(input_change_order_sum, callbacks.client_change.filter(to='change'))
    dp.register_message_handler(get_change_order_sum, state=states.ClientChange.waiting_for_sum)
    dp.register_callback_query_handler(get_no_change_order_sum, callbacks.client_change.filter(to='stay'))
