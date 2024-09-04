import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_broadcaster import TextBroadcaster
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import tgbot.keyboards.inline_permutations_keyboards as inline_keyboards
from tgbot.handlers.main_menu import show_main_menu
from tgbot.keyboards.reply_keyboards import cancel
from tgbot.misc import states, messages, callbacks
from tgbot.services.database.models import User, Mover, MoverOrder
from tgbot.services.bitrix.bitrix_schemas import ExchangeType, DealType


async def start_quick_deal(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer('Введите город приемки Ваших средств', reply_markup=cancel)
    await states.QuickDeal.waiting_for_acceptance_city.set()
    await call.answer()


async def get_acceptance_city(message: Message, state: FSMContext):
    await state.update_data(acceptance_city=message.text)
    await states.QuickDeal.waiting_for_currency.set()
    await message.answer('Выберите валюту, которую отдаете', reply_markup=inline_keyboards.choose_currency)


async def get_quick_deal_currency(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(currency=callback_data['payload'])
    await states.QuickDeal.waiting_for_type.set()
    await call.message.edit_text('Выберите способ оплаты', reply_markup=inline_keyboards.choose_type)
    await call.answer()


async def get_quick_deal_type(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.delete()
    await state.update_data(type=callback_data['payload'])
    async with state.proxy() as data:
        currency = data['currency']
    await states.QuickDeal.waiting_for_sum.set()
    await call.message.answer(f'Введите сумму в {currency}', reply_markup=cancel)
    await call.answer()


async def get_quick_deal_amount(message: Message, state: FSMContext):
    try:
        input_amount = float(message.text)
    except ValueError:
        await message.answer('Неверная сумма. Укажите число.')
        return
    await state.update_data(amount=message.text)
    await states.QuickDeal.waiting_for_country.set()
    await message.answer('Введите страну для получения Ваших средств', reply_markup=cancel)


async def get_quick_deal_country(message: Message, state: FSMContext):
    async_session: AsyncSession = message.bot.get('database')
    await state.update_data(country=message.text)
    await states.QuickDeal.waiting_for_confirm.set()
    async with async_session.begin() as session:
        user = await session.get(User, message.from_id)
    async with state.proxy() as data:
        acceptance_city = data['acceptance_city']
        currency = data['currency']
        amount = data['amount']
    await message.answer(messages.quick_deal_client_message.format(
        name=user.name,
        phone=user.phone,
        username=user.username,
        acceptance_city=acceptance_city,
        country=message.text,
        currency=currency,
        amount=amount
    ), reply_markup=inline_keyboards.confirm_quick_deal)


async def quick_deal_confirm(call: CallbackQuery, callback_data: dict, state: FSMContext):
    async_session: AsyncSession = call.bot.get('database')
    ans = callback_data['payload']
    async with state.proxy() as data:
        acceptance_city = data['acceptance_city']
        currency = data['currency']
        amount = data['amount']
        country = data['country']
    await state.finish()
    if ans == 'yes':
        async with async_session.begin() as session:
            user = await session.get(User, call.from_user.id)
            movers_id = await session.execute(select(Mover.telegram_id))
            movers_id = movers_id.scalars().all()
            mover_order = MoverOrder(
                exchange_type=ExchangeType.RUB_USDT if currency == 'RUB' else ExchangeType.USDT_RUB,
                deal_type=DealType.QUICK_DEAL,
                customer_telegram_id=user.telegram_id,
                acceptance_city=acceptance_city,
                receive_place=country,
                customer_give=float(amount)
            )
            session.add(mover_order)
            mover_order_id = (await session.execute('select max(id) from mover_order')).first()[0]
            if not mover_order_id:
                mover_order_id = 1
            else:
                mover_order_id += 1
        tz = datetime.timezone(datetime.timedelta(hours=7), "Thai")

        msg = messages.quick_deal_mover_message.format(
            mover_order_id=mover_order_id,
            date=datetime.datetime.now(tz=tz).strftime("%d.%m.%Y"),
            name=user.name,
            phone=user.phone,
            username=user.username,
            acceptance_city=acceptance_city,
            country=country,
            currency=currency,
            amount=amount
        )
        await TextBroadcaster(
            chats=movers_id,
            text=msg,
            reply_markup=inline_keyboards.get_mover_order_keyboard(mover_order_id)
        ).run()
        await call.message.edit_text(call.message.text)
        await call.message.answer('Ваша заявка отправлена, наш оператор свяжется с вами в ближайшее время')
    else:
        await call.message.edit_text('Заявка отменена')
    await show_main_menu(call, state)
    await call.answer()


def register_permutations(dp: Dispatcher):
    dp.register_callback_query_handler(start_quick_deal, callbacks.navigation.filter(to='permut_quick_deal'))
    dp.register_message_handler(get_acceptance_city, state=states.QuickDeal.waiting_for_acceptance_city)
    dp.register_callback_query_handler(get_quick_deal_currency, callbacks.navigation.filter(to='choose_cur'),
                                       state=states.QuickDeal.waiting_for_currency)
    dp.register_callback_query_handler(get_quick_deal_type, callbacks.navigation.filter(to='choose_type'),
                                       state=states.QuickDeal.waiting_for_type)
    dp.register_message_handler(get_quick_deal_amount, state=states.QuickDeal.waiting_for_sum)
    dp.register_message_handler(get_quick_deal_country, state=states.QuickDeal.waiting_for_country)
    dp.register_callback_query_handler(quick_deal_confirm, callbacks.navigation.filter(to='quick_confirm'),
                                       state=states.QuickDeal.waiting_for_confirm)
