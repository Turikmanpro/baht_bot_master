import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType
from fast_bitrix24 import BitrixAsync

from tgbot.handlers.exchange import get_custom_fields
from tgbot.keyboards import inline_keyboards, inline
from tgbot.keyboards.inline import get_problem_solved_keyboard, get_send_scan
from tgbot.misc import states, callbacks, messages
from tgbot.misc.helper import is_canceled
from tgbot.services.bitrix.bitrix import change_deal_stage
from tgbot.services.bitrix.bitrix_schemas import SellStage
from tgbot.services.database.models import Order


async def start_scan_input(call: CallbackQuery, callback_data: dict, state: FSMContext):
    db_session = call.message.bot.get('database')
    async with db_session() as session:
        order = await session.get(Order, int(callback_data['order_id']))
        # if order.customer_answered_at:
        #     await call.answer('Вы уже ответили на запрос!', show_alert=True)
        #     return

    if await is_canceled(call.message, order.bitrix_id):
        return

    await call.message.edit_text(call.message.text)
    await call.message.answer('Нажмите скрепку, загрузите фото чека')
    await states.CustomerOrderState.waiting_for_scan.set()
    await state.update_data(order_id=order.bitrix_id, operator_id=order.operator_id)
    await call.answer()


async def cancel_scan_state(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.answer('Отменено!')


async def get_scan(message: Message, state: FSMContext):
    state_data = await state.get_data()
    db_session = message.bot.get('database')
    async with db_session() as session:
        order = await session.get(Order, int(state_data['order_id']))
    if await is_canceled(message, order.bitrix_id):
        return

    currency1, currency2 = order.exchange_type.split('/')
    message_data = [currency1, order.customer_give, currency2, order.customer_receive, order.exchange_rate,
                    order.phone_number, order.customer_name, order.bitrix_id, order.customer.username]
    custom_data = get_custom_fields(order)

    caption = messages.get_message_from_crm(order.exchange_type, order.deal_type, message_data, custom_data)
    caption = 'Скан от пользователя!\n\n' + caption

    if message.document:
        await message.bot.send_document(
            chat_id=state_data['operator_id'],
            document=message.document.file_id,
            caption=caption,
            reply_markup=inline_keyboards.get_order_confirm_keyboard(order_id=state_data['order_id'])
        )
    elif message.photo:
        await message.bot.send_photo(
            chat_id=state_data['operator_id'],
            photo=message.photo[-1]['file_id'],
            caption=caption,
            reply_markup=inline_keyboards.get_order_confirm_keyboard(order_id=state_data['order_id'])
        )

    db_session = message.bot.get('database')
    async with db_session.begin() as session:
        order = await session.get(Order, int(state_data['order_id']))
        order.customer_answered_at = datetime.datetime.now()

    await message.answer('Скан отправлен оператору! Ожидайте')
    await state.finish()


async def report_problem(call: CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('database')
    async with db_session.begin() as session:
        order = await session.get(Order, int(callback_data['order_id']))
        if await is_canceled(call.message, order.bitrix_id):
            return
        if order.customer_answered_at:
            await call.answer('Вы уже ответили на запрос!', show_alert=True)
            return

        order.customer_answered_at = datetime.datetime.now()

    # todo: send to operator that user have a problem

    currency1, currency2 = order.exchange_type.split('/')
    message_data = [currency1, order.customer_give, currency2, order.customer_receive, order.exchange_rate,
                    order.phone_number, order.customer_name, order.bitrix_id, order.customer.username]
    custom_data = get_custom_fields(order)
    await call.message.edit_text(call.message.text)

    msg_text = messages.get_message_from_crm(order.exchange_type, order.deal_type, message_data, custom_data)
    msg_text = f'У пользователя {order.customer_name} проблема!\n\n' + msg_text

    await call.bot.send_message(
        chat_id=order.operator_id,
        text=msg_text,
        reply_markup=get_problem_solved_keyboard(order.bitrix_id)
    )
    await call.answer('Запрос отправлен оператору! Ожидайте звонка', show_alert=True)


async def report_problem2(call: CallbackQuery, callback_data: dict):
    db_session = call.message.bot.get('database')
    async with db_session() as session:
        order = await session.get(Order, int(callback_data['order_id']))
        if await is_canceled(call.message, order.bitrix_id):
            return
        if order.finished:
            await call.answer('Заказ уже завершен!', show_alert=True)
            return

    # todo: send to operator that user have a problem

    currency1, currency2 = order.exchange_type.split('/')
    message_data = [currency1, order.customer_give, currency2, order.customer_receive, order.exchange_rate,
                    order.phone_number, order.customer_name, order.bitrix_id, order.customer.username]
    custom_data = get_custom_fields(order)

    await call.message.edit_text(call.message.text)

    msg_text = messages.get_message_from_crm(order.exchange_type, order.deal_type, message_data, custom_data)
    msg_text = f'У пользователя {order.customer_name} проблема!\n\n' + msg_text

    await call.bot.send_message(
        chat_id=order.operator_id,
        text=msg_text,
        reply_markup=get_problem_solved_keyboard(order.bitrix_id, False)
    )
    await call.answer('Запрос отправлен оператору! Ожидайте звонка', show_alert=True)


async def get_problem_solved(call: CallbackQuery, callback_data: dict, state: FSMContext):
    order_id = int(callback_data['deal_id'])
    db_session = call.message.bot.get('database')
    async with db_session() as session:
        order = await session.get(Order, order_id)
        if await is_canceled(call.message, order.bitrix_id):
            return

    # todo: send to operator that problem solved
    await call.message.edit_text('Проблема решена')

    await call.bot.send_message(order.customer_telegram_id, 'Отправьте скан:', reply_markup=get_send_scan(order_id))

    await call.answer()


async def get_problem_solved2(call: CallbackQuery, callback_data: dict, state: FSMContext):
    order_id = int(callback_data['deal_id'])
    db_session = call.message.bot.get('database')
    async with db_session() as session:
        order = await session.get(Order, order_id)
        if await is_canceled(call.message, order.bitrix_id):
            return
    # todo: send to operator that problem solved
    await call.message.edit_text('Проблема решена')

    await call.bot.send_message(order.customer_telegram_id, 'Проблема решена!\nПодтвердите получение средств',
                                reply_markup=inline.get_receive_confirm_keyboard(order.bitrix_id, False))
    await call.answer()


def register_customer(dp: Dispatcher):
    dp.register_callback_query_handler(report_problem, callbacks.customer_order.filter(action='problem'))
    dp.register_callback_query_handler(report_problem2, callbacks.customer_order.filter(action='problem2'))
    dp.register_callback_query_handler(start_scan_input, callbacks.customer_order.filter(action='load'))
    dp.register_message_handler(get_scan, state=states.CustomerOrderState.waiting_for_scan,
                                content_types=[ContentType.DOCUMENT, ContentType.PHOTO])
    dp.register_callback_query_handler(cancel_scan_state, text='cancel_scan', state=states.CustomerOrderState.waiting_for_scan)
    dp.register_callback_query_handler(get_problem_solved, callbacks.crm_notify.filter(payload='solv_problem'))
    dp.register_callback_query_handler(get_problem_solved2, callbacks.crm_notify.filter(payload='solv_problem2'))
