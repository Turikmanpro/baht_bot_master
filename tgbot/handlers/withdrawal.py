import logging
from decimal import Decimal, ROUND_HALF_DOWN

from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from fast_bitrix24 import BitrixAsync
from sqlalchemy import select
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.handlers.exchange import get_exchange_rate, get_ex_rate_with_percents, get_amounts
from tgbot.keyboards import inline_keyboards, reply_keyboards
from tgbot.keyboards.inline_exchange_keyboards import get_thai_bank_choose_keyboard
from tgbot.misc import callbacks, messages, states
from tgbot.services import AsyncBinance
import tgbot.services.bitrix.create_deals as cd
from tgbot.services.database.models import User, Referral, Order

import tgbot.services.bitrix.bitrix_schemas as b_schemas


async def withdrawal(call: CallbackQuery, callback_data: dict):
    withdraw_type = callback_data['payload']
    minimal_withdrawal = 50
    # todo: get exchange rate rub and thb
    match withdraw_type:
        case 'courier':  # usdt_thb
            # ex_rate = await get_exchange_rate(b_schemas.ExchangeType.USDT_THB)
            # _, minimal_withdrawal = get_amounts(b_schemas.ExchangeType.USDT_THB, 'USDT', Decimal(50), ex_rate)
            text = messages.courier_withdrawal
        case 'rub':  # usdt_rub
            # ex_rate = await get_exchange_rate(b_schemas.ExchangeType.USDT_RUB)
            # _, minimal_withdrawal = get_amounts(b_schemas.ExchangeType.USDT_RUB, 'USDT', Decimal(50), ex_rate)
            text = messages.rub_withdrawal
        case 'usdt':
            text = messages.usdt_withdrawal
        case 'thb':  # usdt_thb
            # ex_rate = await get_exchange_rate(b_schemas.ExchangeType.USDT_THB)
            # _, minimal_withdrawal = get_amounts(b_schemas.ExchangeType.USDT_THB, 'USDT', Decimal(50), ex_rate)
            text = messages.thb_withdrawal
        case _:
            await call.answer('Произошла ошибка, свяжитесь с администратором!', show_alert=True)
            logging.error(f'({call.from_user.id}) unknown withdrawal type: {withdraw_type}')
            return

    db_session = call.bot.get('database')
    async with db_session() as session:
        referral = (await session.execute(select(Referral).where(Referral.telegram_id == int(call.from_user.id)))).first()[0]
        user_referral_balance = referral.ref_balance

    await call.message.edit_text(
        text.format(dividends_sum=user_referral_balance, minimal_sum=minimal_withdrawal),
        reply_markup=inline_keyboards.get_withdrawal_keyboard(withdraw_type)
    )
    await call.answer()


async def withdrawal_confirm(call: CallbackQuery, callback_data: dict, state: FSMContext):
    withdraw_type = callback_data['payload']

    # TODO: get minimal withdrawal sum from db or config
    minimal_withdrawal = 50

    db_session = call.bot.get('database')
    async with db_session() as session:
        referral = \
        (await session.execute(select(Referral).where(Referral.telegram_id == int(call.from_user.id)))).first()[0]
        user_referral_balance = referral.ref_balance

    if minimal_withdrawal > user_referral_balance:
        await call.answer('Недостаточно баланса для вывода!', show_alert=True)
        return

    if withdraw_type == 'courier':
        await call.message.answer('Введите сумму для вывода:', reply_markup=reply_keyboards.cancel)
        await states.WithdrawalState.waiting_for_sum.set()
        await state.update_data(type='courier')

    if withdraw_type == 'rub':
        await call.message.edit_text(
            messages.bank_choose,
            reply_markup=inline_keyboards.get_bank_choose_keyboard('withdraw', back_to='withdraw', back_payload='rub')
        )
    if withdraw_type == 'usdt':
        await call.message.edit_text(messages.token_choose, reply_markup=inline_keyboards.token_choose)
    if withdraw_type == 'thb':
        await call.message.edit_text('Выберите ваш Тайский банк, на который хотите получить THB',
                                     reply_markup=get_thai_bank_choose_keyboard('thb_dividend', 'withdrawal'))

    await call.answer()


async def thb_sum_input(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.delete()
    await call.message.answer('Введите сумму в долларах для получения в THB', reply_markup=reply_keyboards.cancel)
    await states.WithdrawalState.waiting_for_sum.set()
    await state.update_data(bank=callback_data['bank'], type='thb')
    await call.answer()


async def get_withdrawal(message: Message, state: FSMContext):
    db_session = message.bot.get('database')

    withdraw_sum = message.text

    if not withdraw_sum.isdigit():
        await message.answer('Неверная сумма, попробуйте ещё раз:')
        return

    withdraw_sum = int(withdraw_sum)

    data = await state.get_data()
    withdraw_type = data['type']

    async with db_session.begin() as session:
        user = await session.get(User, message.from_id)
        referral = (await session.execute(select(Referral).where(Referral.telegram_id == int(message.from_id)))).first()[0]
        user_referral_balance = referral.ref_balance
        minimal_withdraw = 50

        if minimal_withdraw > withdraw_sum:
            await message.answer('Сумма меньше минимальной, попробуйте ещё раз:')
            return

        if withdraw_sum > user_referral_balance:
            await message.answer('Недостаточно средств, попробуйте ещё раз:')
            return

        referral.ref_balance -= withdraw_sum

        if withdraw_type == 'courier':
            thb_usdt_rate = await AsyncBinance.get_avg_price('THB', 'BUY')
            # TODO: формирование лида на вывод

            await message.answer(
                messages.successful_courier_withdrawal.format(withdrawal_sum=withdraw_sum),
                reply_markup=inline_keyboards.get_back_keyboard()
            )
        elif withdraw_type == 'rub':
            usdt_rub_rate = await AsyncBinance.get_avg_price('RUB', 'BUY', ['TinkoffNew'])
            receive_sum = (usdt_rub_rate * withdraw_sum).quantize(Decimal('1.00'), ROUND_HALF_DOWN)

            bank = data['bank']
            card_number = data['card']

            async with db_session.begin() as session:
                new_order = Order(
                    exchange_type=b_schemas.ExchangeType.USDT_RUB,
                    deal_type=b_schemas.DealType.DIVIDENDS_RUB,
                    customer_name=user.name,
                    customer_telegram_id=message.from_id,
                    phone_number=user.phone,
                    customer_receive=receive_sum,
                    customer_give=withdraw_sum,
                    exchange_rate=usdt_rub_rate,

                    receive_bank=bank,
                    receive_bank_requisites=card_number
                )

                session.add(new_order)

            await message.answer(
                messages.another_currency_dividends_withdrawal.format(
                    withdrawal_sum=withdraw_sum,
                    receive_sum=receive_sum,
                    currency='RUB',
                    exchange_rate=usdt_rub_rate,
                    bank=data['bank'],
                    card_number=data['card']
                ),
                reply_markup=inline_keyboards.get_back_keyboard()
            )
        elif withdraw_type == 'usdt':
            token = data['token']
            wallet = data['wallet']

            async with db_session.begin() as session:
                new_order = Order(
                    exchange_type=b_schemas.ExchangeType.USDT_USDT,
                    deal_type=b_schemas.DealType.DIVIDENDS_USDT,
                    customer_name=user.name,
                    customer_telegram_id=message.from_id,
                    phone_number=user.phone,
                    customer_receive=withdraw_sum,
                    customer_give=withdraw_sum,
                    exchange_rate=1,
                    network_type=wallet,
                    requisites=token
                )

                session.add(new_order)
            await message.answer(
                messages.usdt_dividends_withdrawal.format(
                    withdrawal_sum=withdraw_sum,
                    token=token,
                    wallet=wallet
                ),
                reply_markup=inline_keyboards.get_back_keyboard()
            )
        elif withdraw_type == 'thb':  # usdt_thb
            receive_bank = data['bank']
            # print(data['card'])
            # ex_rate = await get_exchange_rate(b_schemas.ExchangeType.THB_USDT)
            # customer_receive = await get_amounts(b_schemas.ExchangeType.THB_USDT, 'USDT', Decimal(withdraw_sum), ex_rate)
            # main_order_data = [b_schemas.ExchangeType.THB_USDT, b_schemas.DealType.DIVIDENDS_THB, user.name, user.telegram_id, user.phone, customer_receive,
            #                    withdraw_sum, ex_rate]
            # custom_data = {'network_type': '', 'receive_bank': receive_bank,
            #                'receive_bank_requisites': receive_bank_requisites}
            #
            # await message.answer(
            #     messages.another_currency_dividends_withdrawal.format(
            #         withdrawal_sum=withdraw_sum,
            #         receive_sum=receive_sum,
            #         currency='RUB',
            #         exchange_rate=usdt_rub_rate,
            #         bank=receive_bank,
            #         card_number=data['card']
            #     ),
            #     reply_markup=inline_keyboards.get_back_keyboard()
            # )
            await message.answer(
                f'Заявка на вывод в тхб в банк: {receive_bank}',
                reply_markup=inline_keyboards.get_back_keyboard()
            )

    await state.finish()


def register_withdrawal(dp: Dispatcher):
    dp.register_callback_query_handler(withdrawal, callbacks.navigation.filter(to='withdraw'))
    dp.register_callback_query_handler(withdrawal_confirm, callbacks.navigation.filter(to='withdraw_confirm'))
    dp.register_message_handler(get_withdrawal, state=states.WithdrawalState.waiting_for_sum)
    dp.register_callback_query_handler(thb_sum_input, callbacks.bank_choose.filter(type='thb_dividend'))
