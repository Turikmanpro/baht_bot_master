import datetime

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.config import Config
from tgbot.misc.helper import get_rate, get_orig_earned_factor
from tgbot.services.bitrix.get_deals import get_pre_finished_deals, form_deal
from tgbot.services.database.models import Order, Statistic
from tgbot.services.bitrix.bitrix import change_deal_stage

import tgbot.services.bitrix.bitrix_schemas as b_schemas
from tgbot.misc.messages import notify_from_crm, get_message_from_crm, update_rate_input
from tgbot.keyboards.inline import get_notify_keyboard


async def finished_orders_update(bot: Bot, async_session: AsyncSession):
    for deal in deals:
        deal_id = int(deal['ID'])

        async with async_session.begin() as session:
            order = await session.get(Order, deal_id)
            if order and not order.is_received:
                order.is_received = True
            else:
                continue

        deal['contact'] = {'NAME': order.customer_name,
                           'TELEGRAM_ID': order.courier_telegram_id,
                           'PHONE': order.phone_number}

        deal = form_deal(deal)

        async with async_session.begin() as session:
            order = await session.get(Order, deal_id)

            deal_dict = deal.__dict__
            for i in deal_dict:
                setattr(order, i, deal_dict[i])
            if deal.exchange_type == b_schemas.ExchangeType.USDT_RUB:
                order.receive_bank = deal.ru_bank
                order.receive_bank_requisites = deal.ru_bank_requisites
                await bot.send_message(order.customer_telegram_id, notify_from_crm.format(
                    amount=deal.customer_receive,
                    currency=deal.exchange_type.split('/')[1],
                    bank=deal.rub_bank,
                    card_number=deal.rub_bank_requisites
                ), reply_markup=get_notify_keyboard(deal_id))
            elif order.deal_type == b_schemas.DealType.COURIER or order.deal_type == b_schemas.DealType.CASH:
                continue
            else:
                ex_type = order.exchange_type
                deal_type = order.deal_type
                currency1, currency2 = ex_type.split('/')
                message_data = [currency1, order.customer_give, currency2, order.customer_receive, order.exchange_rate,
                                order.phone_number, order.customer_name, order.bitrix_id, order.customer.username]
                if deal_type == b_schemas.DealType.THAI_TRANSFER:
                    sending_bank = order.sending_bank
                    receive_bank = order.receive_bank
                    receive_bank_requisites = order.receive_bank_requisites
                    if ex_type == b_schemas.ExchangeType.RUB_THB:
                        custom_data = {'sending_bank': sending_bank, 'receive_bank': receive_bank,
                                       'receive_bank_requisites': receive_bank_requisites}
                    elif ex_type == b_schemas.ExchangeType.USDT_THB:
                        custom_data = {'network_type': sending_bank, 'receive_bank': receive_bank,
                                       'receive_bank_requisites': receive_bank_requisites}
                    elif ex_type == b_schemas.ExchangeType.THB_USDT:
                        custom_data = {'sending_bank': sending_bank, 'receive_bank': receive_bank,
                                       'receive_bank_requisites': receive_bank_requisites}
                elif deal_type == b_schemas.DealType.RUS_TRANSFER:
                    receive_bank = order.receive_bank
                    receive_bank_requisites = order.receive_bank_requisites
                    if ex_type == b_schemas.ExchangeType.THB_RUB:
                        custom_data = {'receive_bank': receive_bank,
                                       'receive_bank_requisites': receive_bank_requisites}

                user = order.customer
                stat_week = (
                    (await session.execute(
                        select(Statistic).where(Statistic.courier_id == user.referral.original_referral_id,
                                                Statistic.week_created_at - datetime.datetime.now() < datetime.timedelta(
                                                    days=7)))).first())
                if stat_week:
                    stat_id = stat_week[0].id
                else:
                    new_stat = Statistic(courier_id=user.referral.original_referral_id)
                    session.add(new_stat)
                    stat_week = (
                        (await session.execute(
                            select(Statistic).where(Statistic.courier_id == user.referral.original_referral_id,
                                                    Statistic.week_created_at - datetime.datetime.now() < datetime.timedelta(
                                                        days=7)))).first())
                    stat_id = stat_week[0].id
                order.stat_week_id = stat_id
                await bot.send_message(order.customer_telegram_id, update_rate_input, reply_markup=get_notify_keyboard(deal_id))

        print(order.customer_telegram_id)
