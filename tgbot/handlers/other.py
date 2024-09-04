from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select, update

from tgbot.handlers.exchange import get_custom_fields
from tgbot.keyboards import reply_keyboards
from tgbot.misc import messages
from tgbot.services.database.models import User, Order, Courier


async def close(call: CallbackQuery):
    await call.message.delete()
    await call.answer()


async def cancel_state(message: Message, state: FSMContext):
    await state.finish()

    db_session = message.bot.get('database')
    async with db_session() as session:
        user = await session.get(User, message.from_id)
        keyboard = reply_keyboards.get_main_keyboard(show_reg_button=not user.is_reg, is_courier=user.courier)
        order = (await session.execute(select(Order).where(Order.finished == False, Order.is_canceled == False))).first()
        if order:
            order = order[0]
            order_id = order.bitrix_id
            async_session = message.bot.get('database')
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
            # todo: send to operator that order canceled
            if courier_telegram_id:
                # todo: make courier available
                await message.bot.send_message(courier_telegram_id, 'Отмена заявки\n\n' + msg)
            if operator_telegram_id:
                await message.bot.send_message(operator_telegram_id, 'Отмена заявки\n\n' + msg)
            await message.bot.send_message(customer_telegram_id,
                                        'По техническим причинам Ваша заявка отменена. Пожалуйста оформите новую заявку')

        await message.answer(messages.main_menu, reply_markup=keyboard)


async def cancel_state_call(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.answer('Отменено!', show_alert=True)
    await call.message.delete()


async def show_pass(call: CallbackQuery, state: FSMContext):
    await call.answer('Функционал пока недоступен!', show_alert=True)


def register_other(dp: Dispatcher):
    dp.register_callback_query_handler(close, text='close')
    dp.register_message_handler(cancel_state, text='Отмена', state='*')
    dp.register_callback_query_handler(cancel_state_call, text='cancel')
    dp.register_callback_query_handler(show_pass, text='pass', state='*')
