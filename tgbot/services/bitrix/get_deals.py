from fast_bitrix24 import BitrixAsync
from sqlalchemy.ext.asyncio import AsyncSession

import tgbot.services.bitrix.bitrix_schemas as b_schemas
from tgbot.services.database.models import Order


def to_cash_rub_thb_deal(deal_data: dict) -> b_schemas.CashRubThbDeal:
    cf_prefix = 'UF_CRM_'
    contact = deal_data['contact']

    return b_schemas.CashRubThbDeal(
        exchange_type=deal_data[f'{cf_prefix}EXCHANGE_TYPE'],
        deal_type=deal_data[f'{cf_prefix}DEAL_TYPE'],
        customer_name=contact['NAME'],
        telegram_id=contact['TELEGRAM_ID'],
        phone_number=contact['PHONE'],
        customer_receive=float(deal_data[f'{cf_prefix}CUSTOMER_RECEIVE']),
        customer_give=float(deal_data[f'{cf_prefix}CUSTOMER_GIVE']),
        exchange_rate=float(deal_data[f'{cf_prefix}EXCHANGE_RATE']),
        location=deal_data[f'{cf_prefix}LOCATION'],
        ru_bank=deal_data[f'{cf_prefix}SENDING_BANK'],
        location_comment=deal_data[f'{cf_prefix}LOCATION_COMMENT']
    )


def to_cash_usdt_thb_deal(deal_data: dict) -> b_schemas.CashUsdtThbDeal:
    cf_prefix = 'UF_CRM_'
    contact = deal_data['contact']

    return b_schemas.CashUsdtThbDeal(
        exchange_type=deal_data[f'{cf_prefix}EXCHANGE_TYPE'],
        deal_type=deal_data[f'{cf_prefix}DEAL_TYPE'],
        customer_name=contact['NAME'],
        telegram_id=contact['TELEGRAM_ID'],
        phone_number=contact['PHONE'],
        customer_receive=float(deal_data[f'{cf_prefix}CUSTOMER_RECEIVE']),
        customer_give=float(deal_data[f'{cf_prefix}CUSTOMER_GIVE']),
        exchange_rate=float(deal_data[f'{cf_prefix}EXCHANGE_RATE']),
        location=deal_data[f'{cf_prefix}LOCATION'],
        usdt_network=deal_data[f'{cf_prefix}USDT_NETWORK'],
        location_comment=deal_data[f'{cf_prefix}LOCATION_COMMENT']
    )


def to_cash_thb_rub_deal(deal_data: dict) -> b_schemas.CashThbRubDeal:
    cf_prefix = 'UF_CRM_'
    contact = deal_data['contact']

    return b_schemas.CashThbRubDeal(
        exchange_type=deal_data[f'{cf_prefix}EXCHANGE_TYPE'],
        deal_type=deal_data[f'{cf_prefix}DEAL_TYPE'],
        customer_name=contact['NAME'],
        telegram_id=contact['TELEGRAM_ID'],
        phone_number=contact['PHONE'],
        customer_receive=float(deal_data[f'{cf_prefix}CUSTOMER_RECEIVE']),
        customer_give=float(deal_data[f'{cf_prefix}CUSTOMER_GIVE']),
        exchange_rate=float(deal_data[f'{cf_prefix}EXCHANGE_RATE']),
        location=deal_data[f'{cf_prefix}LOCATION'],
        ru_bank=deal_data[f'{cf_prefix}RECEIVE_BANK'],
        ru_bank_requisites=deal_data[f'{cf_prefix}RECEIVE_BANK_REQUISITES'],
        location_comment=deal_data[f'{cf_prefix}LOCATION_COMMENT']
    )


def to_cash_thb_usdt_deal(deal_data: dict) -> b_schemas.CashThbUsdtDeal:
    cf_prefix = 'UF_CRM_'
    contact = deal_data['contact']

    return b_schemas.CashThbUsdtDeal(
        exchange_type=deal_data[f'{cf_prefix}EXCHANGE_TYPE'],
        deal_type=deal_data[f'{cf_prefix}DEAL_TYPE'],
        customer_name=contact['NAME'],
        telegram_id=contact['TELEGRAM_ID'],
        phone_number=contact['PHONE'],
        customer_receive=float(deal_data[f'{cf_prefix}CUSTOMER_RECEIVE']),
        customer_give=float(deal_data[f'{cf_prefix}CUSTOMER_GIVE']),
        exchange_rate=float(deal_data[f'{cf_prefix}EXCHANGE_RATE']),
        location=deal_data[f'{cf_prefix}LOCATION'],
        usdt_network=deal_data[f'{cf_prefix}USDT_NETWORK'],
        usdt_requisites=deal_data[f'{cf_prefix}USDT_REQUISITES'],
        location_comment=deal_data[f'{cf_prefix}LOCATION_COMMENT']
    )


def to_rub_thb_deal(deal_data: dict) -> b_schemas.RubThbDeal:
    cf_prefix = 'UF_CRM_'
    contact = deal_data['contact']

    return b_schemas.RubThbDeal(
        exchange_type=deal_data[f'{cf_prefix}EXCHANGE_TYPE'],
        deal_type=deal_data[f'{cf_prefix}DEAL_TYPE'],
        customer_name=contact['NAME'],
        telegram_id=contact['TELEGRAM_ID'],
        phone_number=contact['PHONE'],
        customer_receive=float(deal_data[f'{cf_prefix}CUSTOMER_RECEIVE']),
        customer_give=float(deal_data[f'{cf_prefix}CUSTOMER_GIVE']),
        exchange_rate=float(deal_data[f'{cf_prefix}EXCHANGE_RATE']),
        rub_bank=deal_data[f'{cf_prefix}SENDING_BANK'],
        thb_bank=deal_data[f'{cf_prefix}RECEIVE_BANK'],
        thb_bank_requisites=deal_data[f'{cf_prefix}RECEIVE_BANK_REQUISITES']
    )


def to_usdt_thb_deal(deal_data: dict) -> b_schemas.UsdtThbDeal:
    cf_prefix = 'UF_CRM_'
    contact = deal_data['contact']

    return b_schemas.UsdtThbDeal(
        exchange_type=deal_data[f'{cf_prefix}EXCHANGE_TYPE'],
        deal_type=deal_data[f'{cf_prefix}DEAL_TYPE'],
        customer_name=contact['NAME'],
        telegram_id=contact['TELEGRAM_ID'],
        phone_number=contact['PHONE'],
        customer_receive=float(deal_data[f'{cf_prefix}CUSTOMER_RECEIVE']),
        customer_give=float(deal_data[f'{cf_prefix}CUSTOMER_GIVE']),
        exchange_rate=float(deal_data[f'{cf_prefix}EXCHANGE_RATE']),
        usdt_network=deal_data[f'{cf_prefix}USDT_NETWORK'],
        usdt_requisites=deal_data[f'{cf_prefix}USDT_REQUISITES'],
        thai_bank=deal_data[f'{cf_prefix}RECEIVE_BANK'],
        thai_bank_requisites=deal_data[f'{cf_prefix}RECEIVE_BANK_REQUISITES']
    )


def to_thb_rub_deal(deal_data: dict) -> b_schemas.ThbRubDeal:
    cf_prefix = 'UF_CRM_'
    contact = deal_data['contact']

    return b_schemas.ThbRubDeal(
        exchange_type=deal_data[f'{cf_prefix}EXCHANGE_TYPE'],
        deal_type=deal_data[f'{cf_prefix}DEAL_TYPE'],
        customer_name=contact['NAME'],
        telegram_id=contact['TELEGRAM_ID'],
        phone_number=contact['PHONE'],
        customer_receive=float(deal_data[f'{cf_prefix}CUSTOMER_RECEIVE']),
        customer_give=float(deal_data[f'{cf_prefix}CUSTOMER_GIVE']),
        exchange_rate=float(deal_data[f'{cf_prefix}EXCHANGE_RATE']),
        thb_bank=deal_data[f'{cf_prefix}SENDING_BANK'],
        ru_bank=deal_data[f'{cf_prefix}RECEIVE_BANK'],
        ru_bank_requisites=deal_data[f'{cf_prefix}RECEIVE_BANK_REQUISITES']
    )


def to_thb_usdt_deal(deal_data: dict) -> b_schemas.ThbUsdtDeal:
    cf_prefix = 'UF_CRM_'
    contact = deal_data['contact']

    return b_schemas.ThbUsdtDeal(
        exchange_type=deal_data[f'{cf_prefix}EXCHANGE_TYPE'],
        deal_type=deal_data[f'{cf_prefix}DEAL_TYPE'],
        customer_name=contact['NAME'],
        telegram_id=contact['TELEGRAM_ID'],
        phone_number=contact['PHONE'],
        customer_receive=float(deal_data[f'{cf_prefix}CUSTOMER_RECEIVE']),
        customer_give=float(deal_data[f'{cf_prefix}CUSTOMER_GIVE']),
        exchange_rate=float(deal_data[f'{cf_prefix}EXCHANGE_RATE']),
        thb_bank=deal_data[f'{cf_prefix}RECEIVE_BANK'],
        usdt_network=deal_data[f'{cf_prefix}USDT_NETWORK'],
        usdt_requisites=deal_data[f'{cf_prefix}USDT_REQUISITES'],
    )


def to_usdt_rub_deal(deal_data: dict) -> b_schemas.UsdtRubDeal:
    cf_prefix = 'UF_CRM_'
    contact = deal_data['contact']

    return b_schemas.UsdtRubDeal(
        exchange_type=deal_data[f'{cf_prefix}EXCHANGE_TYPE'],
        deal_type=deal_data[f'{cf_prefix}DEAL_TYPE'],
        customer_name=contact['NAME'],
        telegram_id=contact['TELEGRAM_ID'],
        phone_number=contact['PHONE'],
        customer_receive=float(deal_data[f'{cf_prefix}CUSTOMER_RECEIVE']),
        customer_give=float(deal_data[f'{cf_prefix}CUSTOMER_GIVE']),
        exchange_rate=float(deal_data[f'{cf_prefix}EXCHANGE_RATE']),
        rub_bank=deal_data[f'{cf_prefix}RECEIVE_BANK'],
        rub_bank_requisites=deal_data[f'{cf_prefix}RECEIVE_BANK_REQUISITES']
    )


def form_deal(deal_data: dict):
    cf_prefix = 'UF_CRM_'
    exchange_type = deal_data[f'{cf_prefix}EXCHANGE_TYPE']
    deal_type = deal_data[f'{cf_prefix}DEAL_TYPE']

    if deal_type == b_schemas.DealType.THAI_TRANSFER:
        if exchange_type == b_schemas.ExchangeType.RUB_THB:
            return to_rub_thb_deal(deal_data)
        elif exchange_type == b_schemas.ExchangeType.USDT_THB:
            return to_usdt_thb_deal(deal_data)
        elif exchange_type == b_schemas.ExchangeType.THB_USDT:
            return to_thb_usdt_deal(deal_data)
    elif deal_type == b_schemas.DealType.RUS_TRANSFER:
        if exchange_type == b_schemas.ExchangeType.THB_RUB:
            return to_thb_rub_deal(deal_data)
        elif exchange_type == b_schemas.ExchangeType.USDT_RUB:
            return to_usdt_rub_deal(deal_data)
    elif deal_type == b_schemas.DealType.COURIER:
        if exchange_type == b_schemas.ExchangeType.USDT_THB:
            return to_cash_usdt_thb_deal(deal_data)
    elif deal_type == b_schemas.DealType.CASH:
        if exchange_type == b_schemas.ExchangeType.RUB_THB:
            return to_cash_rub_thb_deal(deal_data)
        elif exchange_type == b_schemas.ExchangeType.THB_RUB:
            return to_cash_thb_rub_deal(deal_data)
        elif exchange_type == b_schemas.ExchangeType.THB_USDT:
            return to_cash_thb_usdt_deal(deal_data)


async def get_deal(bitrix: BitrixAsync, async_session: AsyncSession, deal_id: int):
    deal_data = await bitrix.call('crm.deal.get', {'id': deal_id})

    async with async_session.begin() as session:
        order = await session.get(Order, deal_id)

    deal_data['contact'] = {'NAME': order.customer_name,
                            'TELEGRAM_ID': order.customer_telegram_id,
                            'PHONE': order.phone_number}

    return form_deal(deal_data)


async def get_pre_finished_deals(bitrix: BitrixAsync):
    deals = await bitrix.get_all('crm.deal.list', {
        'filter': {'STAGE_ID': b_schemas.SellStage.EXCHANGE},
        'select': ['*', 'UF_*']
    })

    return deals
