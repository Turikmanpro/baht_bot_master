import datetime

from aiogram import Bot
from aiogram_broadcaster import TextBroadcaster

from tgbot.config import Config
from tgbot.misc.helper import get_rate
from tgbot.misc.messages import ex_rate_update
from tgbot.keyboards.inline import get_courier_arrived_keyboard, get_courier_on_the_way_keyboard
from tgbot.services.bitrix.get_deals import get_deal
from tgbot.services.database.models import Courier, Order, Statistic, User
from tgbot.services.bitrix.bitrix import get_couriers_for_delivery, change_deal_stage, change_courier_availability, \
    get_courier_delivery_message
from tgbot.services.bitrix.bitrix_schemas import SellStage, ExchangeType

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert


async def delivery_update(bot: Bot, async_session: AsyncSession, config: Config):
    bitrix = bot.get('bitrix')
    config = bot.get('config')

    delivery_data = await get_couriers_for_delivery(bitrix)

    async with async_session.begin() as session:
        for courier in delivery_data:
            order = await session.get(Order, int(courier['deal_id']))
            if order:
                order.courier_telegram_id = int(courier['courier_id'])

                stat_week = ((await session.execute(select(Statistic).where(Statistic.courier_id == int(courier['courier_id']), Statistic.week_created_at-datetime.datetime.now() < datetime.timedelta(days=7)))).first())
                if not stat_week:
                    week_day = datetime.datetime.weekday(datetime.datetime.now())
                    new_stat_week = Statistic(
                        courier_id=int(courier['courier_id']),
                        week_created_at=datetime.datetime.now() - datetime.timedelta(days=abs(week_day))
                    )
                    a = session.add(new_stat_week)
                    stat_week = ((await session.execute(select(Statistic).where(Statistic.courier_id == int(courier['courier_id']), Statistic.week_created_at-datetime.datetime.now() < datetime.timedelta(days=7)))).first())

                order.stat_week_id = stat_week[0].id
                # get from config delivery percent and translate sum to usdt

                order.courier_earn = await get_rate(order.customer_give, 0.01, order.exchange_type)

                courier_data = await session.get(Courier, int(courier['courier_id']))
                user = await session.get(User, int(courier['courier_id']))

                await change_deal_stage(bitrix, SellStage.WAITING_FOR_DELIVERY, int(courier['deal_id']))

                await change_courier_availability(bitrix, courier_data.product_id, user.name, True)

                # send notify to courier
                deal = await get_deal(bitrix, async_session, order.bitrix_id)
                message_text = get_courier_delivery_message(deal, order.customer.username, order.bitrix_id)
                await bot.send_message(order.courier_telegram_id, message_text, reply_markup=get_courier_on_the_way_keyboard(order.bitrix_id))

