import asyncio

import aioschedule
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from tgbot.config import Config
from tgbot.services.schedulers.statistic_update import delivery_update
from tgbot.services.schedulers.finished_orders_update import finished_orders_update


async def start_schedulers(config: Config, bot: Bot, session: sessionmaker):
    aioschedule.every(1).minutes.do(delivery_update, bot, session, config)
    aioschedule.every(1).minutes.do(finished_orders_update, bot, session)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
