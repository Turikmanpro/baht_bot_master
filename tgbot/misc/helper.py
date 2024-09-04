import asyncio
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from tgbot.config import load_config
from tgbot.services import AsyncBinance
from tgbot.services.bitrix.bitrix_schemas import ExchangeType
from tgbot.services.database.base import Base
from tgbot.services.database.models import Referral, Order


async def is_canceled(message, order_id, text='Заказ отменен. Оформите новый, если хотите продолжить!'):
    async_session: AsyncSession = message.bot.get('database')
    async with async_session.begin() as session:
        order = await session.get(Order, order_id)
    if order.is_canceled:
        await message.edit_text(text)
        return True
    return False


async def get_ref(session, telegram_id):
    return ((await session.execute(select(Referral).where(Referral.telegram_id == telegram_id))).first())[0]


async def add_ref_stats(async_session, ref_id, amount):
    async with async_session.begin() as session:
        ref = await session.get(Referral, ref_id)
        ref.ref_balance += amount
        ref.red_deposit += amount

        if ref.senior_referral_id is not None:
            return ref.senior_referral_id


async def get_rate(amount, factor, ex_type):
    # translate to usdt
    amount = Decimal(amount)
    factor = Decimal(factor)
    if ex_type == ExchangeType.THB_RUB or ex_type == ExchangeType.THB_USDT:  # amount in thb
        ex_rate = await AsyncBinance.get_avg_price('THB', 'SELL')
        amount = (amount / ex_rate).quantize(Decimal('1.000'))
    elif ex_type == ExchangeType.RUB_THB:  # amount in rub
        ex_rate = await AsyncBinance.get_avg_price('RUB', 'SELL')
        amount = (amount / ex_rate).quantize(Decimal('1.000'))
    return (amount * factor).quantize(Decimal('1.000'))


async def send_ref_info(bot, telegram_id, amount):
    await bot.send_message(
        chat_id=telegram_id,
        text=f'Вам начислены дивиденды от сделки в размере: {amount} USD',
    )


async def all_ref_stat(bot, async_session, order):
    orig_level_factor = 0.015
    lvl1_factor = 0.005
    lvl2_factor = 0.003
    lvl3_factor = 0.002
    async with async_session.begin() as session:
        customer_referral_account = await get_ref(session, order.customer_telegram_id)
        customer_referral_account.deals_count += 1
        level = customer_referral_account.level
        print(f'all_ref_stat | ref {customer_referral_account.telegram_id} | level {level}')
        if level == 1:
            amount = float(await get_rate(order.customer_give, 0.025, order.exchange_type))
            await add_ref_stats(async_session, customer_referral_account.senior_referral_id, amount)
            print(f'orig level amount {amount}')
            ref = await session.get(Referral, customer_referral_account.senior_referral_id)
            ref.ref_deals_count += 1
        elif level == 2:
            # lvl 1
            amount = float(await get_rate(order.customer_give, lvl1_factor, order.exchange_type))
            orig_ref_id = await add_ref_stats(async_session, customer_referral_account.senior_referral_id, amount)
            ref = await session.get(Referral, customer_referral_account.senior_referral_id)
            ref.lvl1_ref_balance += amount
            ref.ref_deals_count += 1
            print(f'lvl 1 amount {amount}')
            await send_ref_info(bot, ref.telegram_id, amount)

            # orig level
            amount = float(await get_rate(order.customer_give, 0.02, order.exchange_type))
            await add_ref_stats(async_session, orig_ref_id, amount)
            ref = await session.get(Referral, orig_ref_id)
            ref.ref_deals_count += 1
            print(f'orig level amount {amount}')
        elif level == 3:
            # lvl 1
            amount = float(await get_rate(order.customer_give, lvl1_factor, order.exchange_type))
            lvl1_ref_id = await add_ref_stats(async_session, customer_referral_account.senior_referral_id, amount)

            ref = await session.get(Referral, customer_referral_account.senior_referral_id)
            ref.lvl1_ref_balance += amount
            ref.ref_deals_count += 1
            print(f'lvl 1 amount {amount}')
            await send_ref_info(bot, ref.telegram_id, amount)

            # lvl 2
            amount = float(await get_rate(order.customer_give, lvl2_factor, order.exchange_type))
            orig_ref_id = await add_ref_stats(async_session, lvl1_ref_id, amount)

            ref = await session.get(Referral, lvl1_ref_id)
            ref.lvl2_ref_balance += amount
            ref.ref_deals_count += 1
            print(f'lvl 2 amount {amount}')
            await send_ref_info(bot, ref.telegram_id, amount)

            # orig level
            amount = float(await get_rate(order.customer_give, 0.017, order.exchange_type))
            await add_ref_stats(async_session, orig_ref_id, amount)

            ref = await session.get(Referral, orig_ref_id)
            ref.ref_deals_count += 1
            print(f'orig level amount {amount}')
        else:
            # lvl 1
            amount = float(await get_rate(order.customer_give, lvl1_factor, order.exchange_type))
            lvl2_ref_id = await add_ref_stats(async_session, customer_referral_account.senior_referral_id, amount)

            ref = await session.get(Referral, customer_referral_account.senior_referral_id)
            ref.lvl1_ref_balance += amount
            ref.ref_deals_count += 1
            print(f'lvl 1 amount {amount}')
            await send_ref_info(bot, ref.telegram_id, amount)

            # lvl 2
            amount = float(await get_rate(order.customer_give, lvl2_factor, order.exchange_type))
            lvl1_ref_id = await add_ref_stats(async_session, lvl2_ref_id, amount)

            ref = await session.get(Referral, lvl2_ref_id)
            ref.lvl2_ref_balance += amount
            ref.ref_deals_count += 1
            print(f'lvl 2 amount {amount}')
            await send_ref_info(bot, ref.telegram_id, amount)

            # lvl 3
            amount = float(await get_rate(order.customer_give, lvl3_factor, order.exchange_type))
            orig_ref_id = await add_ref_stats(async_session, lvl1_ref_id, amount)

            ref = await session.get(Referral, lvl1_ref_id)
            ref.lvl3_ref_balance += amount
            ref.ref_deals_count += 1
            print(f'lvl 3 amount {amount}')
            await send_ref_info(bot, ref.telegram_id, amount)

            orig_ref = await session.get(Referral, orig_ref_id)
            orig_ref = await session.get(Referral, orig_ref.original_referral_id)
            orig_ref.ref_deals_count += 1

            # orig level
            amount = float(await get_rate(order.customer_give, orig_level_factor, order.exchange_type))
            await add_ref_stats(async_session, orig_ref.original_referral_id, amount)
            print(f'orig level amount {amount}')


def get_orig_earned_factor(level):
    if level == 1:
        return 0.025
    elif level == 2:
        return 0.02
    elif level == 3:
        return 0.017
    else:
        return 0.015


def get_ref_lvl_earned_factor(level, is_default):
    if is_default:
        return 0.025
    if level == 1:
        return 0.005
    elif level == 2:
        return 0.003
    elif level == 3:
        return 0.002
    else:
        return 0.0
