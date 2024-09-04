import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aioredis import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tgbot import filters
from tgbot import handlers
from tgbot import middlewares
from tgbot.config import load_config, save_config
from tgbot.handlers.other import show_pass
from tgbot.services.database.base import Base
from tgbot.services.database.models import Referral, User, Courier, Button
from tgbot.services.mailing import AsyncMail

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    dp.setup_middleware(middlewares.EnvironmentMiddleware(config=config))
    dp.setup_middleware(middlewares.ThrottlingMiddleware())


def register_all_filters(dp):
    for aiogram_filter in filters.filters:
        dp.filters_factory.bind(aiogram_filter)


def register_all_handlers(dp):
    for register_handler in handlers.register_functions:
        register_handler(dp)
    dp.register_callback_query_handler(show_pass)  # During development


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
        handlers=(logging.FileHandler(r'logs.log'), logging.StreamHandler())
    )

    logger.info('Starting bot')
    config = load_config('.env')

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot_info = await bot.get_me()
    logger.info(f'Bot - {bot_info.mention}')

    redis = Redis()
    mail = AsyncMail(config.mailing.host, config.mailing.user, config.mailing.password, config.mailing.use_TLS,
                     config.mailing.port)

    engine = create_async_engine(
        f'postgresql+asyncpg://{config.db.user}:{config.db.password}@'
        f'{config.db.host}:{config.db.port}/{config.db.database}',
        future=True
    )
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    await User.create_default_users(async_sessionmaker)
    await Referral.create_default_referrals(async_sessionmaker)
    await Courier.create_default_couriers(async_sessionmaker)
    await Button.insert_buttons(async_sessionmaker)

    bot['config'] = config
    bot['redis'] = redis
    bot['database'] = async_sessionmaker
    bot['mail'] = mail

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    try:
        await dp.start_polling()
    finally:
        save_config(config.misc.config_path, config.misc.transfer_percent, config.misc.delivery_percent)
        bot_session = await bot.get_session()
        await bot_session.close()
        await dp.storage.close()
        await dp.storage.wait_closed()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped!')
        raise 
