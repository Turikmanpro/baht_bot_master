import json
import os
from dataclasses import dataclass
from pathlib import Path

import aiofiles.os
from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: str


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool


@dataclass
class Miscellaneous:
    bitrix_webhook: str
    items_per_page: int
    delivery_percent: float
    transfer_percent: float
    config_path: Path
    reviews_channel_url: str


@dataclass
class Mailing:
    use_TLS: bool
    host: str
    password: str
    user: str
    port: int


@dataclass
class VideosId:
    start: str
    earn_usdt: str
    courier: str
    non_cash: str
    non_cash_back: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous
    mailing: Mailing
    videos_id: VideosId


def save_config(config_path, transfer_percent=2.5, delivery_percent=3.5):
    config_data = {
        'delivery_percent': delivery_percent,
        'transfer_percent': transfer_percent
    }

    with open(config_path, 'w') as file:
        json.dump(config_data, file, indent=4)

    return transfer_percent, delivery_percent


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    config_path = Path(__file__).parent / 'config.json'
    if not config_path.is_file():
        transfer_percent, delivery_percent = save_config(config_path)
    else:
        with open(config_path, 'r') as file:
            config_data = json.load(file)
        transfer_percent, delivery_percent = config_data['transfer_percent'], config_data['delivery_percent']

    return Config(
        tg_bot=TgBot(
            token=env.str('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMINS'))),
            use_redis=env.bool('USE_REDIS'),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME'),
            port=env.str('DB_PORT')
        ),
        misc=Miscellaneous(
            bitrix_webhook=env.str('BITRIX_WEBHOOK'),
            items_per_page=env.int('ITEMS_PER_PAGE'),
            transfer_percent=transfer_percent,
            delivery_percent=delivery_percent,
            config_path=config_path,
            reviews_channel_url=env.str('REVIEWS_CHANNEL_URL')
        ),
        mailing=Mailing(
            use_TLS=env.bool('USE_TLS'),
            host=env.str('MAIL_HOST'),
            password=env.str('MAIL_PASS'),
            user=env.str('MAIL_USER'),
            port=env.int('MAIL_PORT')
        ),
        videos_id=VideosId(
            start=env.str('START_FILE_ID'),
            earn_usdt=env.str('EARN_USDT'),
            courier=env.str('COURIER'),
            non_cash=env.str('NON_CASH'),
            non_cash_back=env.str('NON_CASH_BACK')
        )
    )
