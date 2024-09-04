import datetime
import aiohttp
import asyncio

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_broadcaster import TextBroadcaster
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

import tgbot.keyboards.inline_permutations_keyboards as inline_keyboards
from tgbot.handlers.exchange import get_exchange_rate, get_amounts
from tgbot.handlers.main_menu import show_main_menu
from tgbot.keyboards.reply_keyboards import cancel
from tgbot.misc import states, messages, callbacks
from tgbot.services import AsyncBinance
from tgbot.services.database.models import User, Mover, MoverOrder
from tgbot.services.bitrix.bitrix_schemas import ExchangeType, DealType


async def deal_calc(call: CallbackQuery):
    await call.message.edit_text('Выберите валюту, которую отдаете', reply_markup=inline_keyboards.choose_currency)
    await states.OftenMoversDeal.waiting_for_currency.set()
    await call.answer()


async def get_currency(call: CallbackQuery, callback_data: dict, state: FSMContext):
    currency = callback_data['payload']
    if currency == 'USD':
        await call.answer('Временно в разработке', show_alert=True)
        return
    await state.update_data(currency=callback_data['payload'])
    await states.OftenMoversDeal.waiting_for_currency.set()
    await call.message.edit_text('Выберите офис приемки Ваших средств',
                                 reply_markup=inline_keyboards.often_deal_receiving_office)
    await call.answer()


async def get_receiving_office(call: CallbackQuery, callback_data: dict, state: FSMContext):
    receiving_office = callback_data['payload']
    await state.update_data(receiving_office=receiving_office)
    await states.OftenMoversDeal.waiting_for_currency.set()
    await call.message.edit_text('Выберите способ оплаты', reply_markup=inline_keyboards.choose_type)
    await call.answer()


async def get_deal_type(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await state.update_data(type=callback_data['payload'])
    await states.OftenMoversDeal.waiting_for_currency.set()
    await call.message.edit_text('Выберите страну для получения Ваших средств',
                                 reply_markup=inline_keyboards.often_deal_country_choose)
    await call.answer()


async def get_deal_amount(message: Message, state: FSMContext):
    async_session: AsyncSession = message.bot.get('database')
    try:
        input_amount = float(message.text)
    except ValueError:
        await message.answer('Неверная сумма. Укажите число.')
        return
    await state.update_data(amount=message.text)

    await states.OftenMoversDeal.waiting_for_confirm.set()
    async with state.proxy() as data:
        receiving_office = data['receiving_office']
        currency = data['currency']
        amount = data['amount']
        country = data['country']
        city = data['city']
    async with async_session.begin() as session:
        user = await session.get(User, message.from_user.id)
    ex_rate = await get_exchange_rate(ExchangeType.RUB_THB)
    amount, amount2 = get_amounts(ExchangeType.RUB_THB, 'RUB', Decimal(amount), ex_rate)
    await state.update_data(amount2=amount2, ex_rate=ex_rate)
    msg = messages.often_deal_client_message.format(
        name=user.name,
        phone=user.phone,
        username=user.username,
        acceptance_city=convert_to_full_names(city),
        country=f'{convert_to_full_names(country)} - {convert_to_full_names(receiving_office)}',
        currency=currency,
        amount=amount,
        amount_2=amount2,
        ex_rate=ex_rate
    )
    await message.answer(msg, reply_markup=inline_keyboards.confirm_quick_deal)


async def get_deal_country(call: CallbackQuery, callback_data: dict, state: FSMContext):
    country = callback_data['payload']
    await state.update_data(country=country)
    await states.OftenMoversDeal.waiting_for_currency.set()
    await call.message.edit_text('Выберите город', reply_markup=inline_keyboards.often_deal_city_choose)
    await call.answer()


async def get_garantex_ex_rate():
    async with aiohttp.ClientSession() as session:
        fee = 0
        async with await session.get('https://garantex.io/api/v2/markets') as response:
            response = await response.json()
            for i in response:
                if i['id'] == 'usdtrub':
                    fee = float(i['maker_fee'])
        async with await session.get('https://garantex.io/api/v2/trades?market=usdtrub') as response:
            response = await response.json()
            if response:
                return round(float(response[0]['price']) + float(response[0]['price']) * fee, 2)


async def get_often_mover_deal_ex_rate(percent, amount_usdt):
    if 20000 > amount_usdt >= 10000:
        amount_percent = 0.02
    elif 40000 > amount_usdt >= 20000:
        amount_percent = 0.016
    elif 70000 > amount_usdt >= 40000:
        amount_percent = 0.014
    elif 100000 > amount_usdt >= 70000:
        amount_percent = 0.012
    elif 100000 >= amount_usdt:
        amount_percent = 0.01
    else:
        amount_percent = 0

    garantex_ex_rate = await get_garantex_ex_rate()
    binance_ex_rate1 = float(await AsyncBinance.get_avg_price('THB', 'SELL'))
    binance_ex_rate_p2p_sell = binance_ex_rate1
    temp = (garantex_ex_rate + garantex_ex_rate * percent) / binance_ex_rate1
    temp = temp - 2.2227 + binance_ex_rate_p2p_sell
    temp = temp + temp * amount_percent
    return round(temp, 2)


async def main():
    print(await get_often_mover_deal_ex_rate(0.7, 1000))


if __name__ == '__main__':
    asyncio.run(main())


def convert_to_full_names(text) -> str:
    match text:
        case 'ph':
            return 'Пхукет'
        case 'tai':
            return 'Тайланд'
        case 'msk':
            return 'Москва'


async def get_deal_city(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.delete()
    city = callback_data['payload']
    async with state.proxy() as data:
        currency = data['currency']
    await state.update_data(city=city)
    await call.message.answer(f'Введите сумму в {currency}', reply_markup=cancel)
    await states.OftenMoversDeal.waiting_for_sum.set()
    await call.answer()


async def get_confirm(call: CallbackQuery, callback_data: dict, state: FSMContext):
    async_session: AsyncSession = call.bot.get('database')
    ans = callback_data['payload']
    async with state.proxy() as data:
        receiving_office = data['receiving_office']
        currency = data['currency']
        amount = data['amount']
        country = data['country']
        city = data['city']
        amount2 = data['amount2']
        ex_rate = data['ex_rate']
    await state.finish()
    if ans == 'yes':
        async with async_session.begin() as session:
            # get percents for each receiving_office
            user = await session.get(User, call.from_user.id)
            movers_id = await session.execute(select(Mover.telegram_id))
            movers_id = movers_id.scalars().all()
            mover_order = MoverOrder(
                exchange_type=ExchangeType.RUB_USDT if currency == 'RUB' else ExchangeType.USDT_RUB,
                deal_type=DealType.OFTEN_DEAL,
                customer_telegram_id=user.telegram_id,
                acceptance_city=receiving_office,
                receive_place=f'{country}-{city}',
                customer_give=float(amount),
                customer_receive=float(amount2),
                exchange_rate=float(ex_rate)
            )
            session.add(mover_order)
        async with async_session.begin() as session:
            mover_order_id = (await session.execute('select max(id) from mover_order')).first()[0]
        tz = datetime.timezone(datetime.timedelta(hours=7), "Thai")

        msg = messages.often_deal_mover_message.format(
            mover_order_id=mover_order_id,
            date=datetime.datetime.now(tz=tz).strftime("%d.%m.%Y"),
            name=user.name,
            phone=user.phone,
            username=user.username,
            acceptance_city=convert_to_full_names(city),
            country=f'{convert_to_full_names(country)} - {convert_to_full_names(receiving_office)}',
            currency=currency,
            amount=amount,
            amount_2=amount2,
            ex_rate=ex_rate
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


def register_permutations_deal_calc(dp: Dispatcher):
    dp.register_callback_query_handler(deal_calc, callbacks.navigation.filter(to='permut_deal_calc'), state='*')
    dp.register_callback_query_handler(get_currency, callbacks.navigation.filter(to='choose_cur'),
                                       state=states.OftenMoversDeal.waiting_for_currency)
    dp.register_callback_query_handler(get_receiving_office, callbacks.navigation.filter(to='receiving_office'),
                                       state=states.OftenMoversDeal.waiting_for_currency)
    dp.register_callback_query_handler(get_deal_type, callbacks.navigation.filter(to='choose_type'),
                                       state=states.OftenMoversDeal.waiting_for_currency)

    dp.register_callback_query_handler(get_deal_country, callbacks.navigation.filter(to='often_country_choose'),
                                       state=states.OftenMoversDeal.waiting_for_currency)
    dp.register_callback_query_handler(get_deal_city, callbacks.navigation.filter(to='often_city_choose'),
                                       state=states.OftenMoversDeal.waiting_for_currency)

    dp.register_message_handler(get_deal_amount, state=states.OftenMoversDeal.waiting_for_sum)

    dp.register_callback_query_handler(get_confirm, callbacks.navigation.filter(to='quick_confirm'),
                                       state=states.OftenMoversDeal.waiting_for_confirm)
