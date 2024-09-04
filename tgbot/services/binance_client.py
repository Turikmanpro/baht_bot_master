import asyncio
from decimal import Decimal, ROUND_HALF_DOWN
from pprint import pprint

import aiohttp


class AsyncBinance:
    p2p_api_url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'

    @classmethod
    async def get_p2p_sellers(cls, asset: str, fiat: str, trade_type: str, pay_types: list = None, rows=16):
        """
        Getting Sellers and Prices with Binance P2P

        :param asset:
        :param fiat:
        :param trade_type:
        :param pay_types:
        :param rows:
        :return:
        """
        body = {
            "proMerchantAds": False,
            "page": 1,
            "rows": rows,
            "payTypes": pay_types,
            "countries": [],
            "publisherType": None,
            "asset": asset,
            "fiat": fiat,
            "tradeType": trade_type
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(cls.p2p_api_url, json=body) as response:
                if response.ok:
                    return (await response.json())['data']
                raise ConnectionError

    @classmethod
    async def get_rub_thb_exchange_rate(cls):
        usdt_avg_price = await cls.get_avg_price('RUB', 'BUY', ['TinkoffNew'])
        thb_avg_price = await cls.get_avg_price('THB', 'SELL')

        return (usdt_avg_price / thb_avg_price).quantize(Decimal('1.000'), ROUND_HALF_DOWN)

    @classmethod
    async def get_avg_price(cls, fiat: str, trade_type: str, pay_types: list = None, first=6, last=16):
        sellers = await cls.get_p2p_sellers('USDT', fiat, trade_type, pay_types, rows=last)
        sellers = sellers[first - 1:last]
        price_sum = sum(map(Decimal, (seller['adv']['price'] for seller in sellers)))

        avg_price = (price_sum / len(sellers)).quantize(Decimal('1.000'), ROUND_HALF_DOWN)

        return avg_price


async def main():
    rub_thb = await AsyncBinance.get_rub_thb_exchange_rate()
    thb_avg_price = await AsyncBinance.get_avg_price('THB', 'SELL')  # usdt_thb
    print(thb_avg_price)
    print(1 / thb_avg_price)

    print(rub_thb)
    print(await AsyncBinance.get_avg_price('THB', 'SELL'))


if __name__ == "__main__":
    asyncio.run(main())
