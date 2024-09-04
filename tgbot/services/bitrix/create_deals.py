from fast_bitrix24 import BitrixAsync

import tgbot.services.bitrix.bitrix_schemas as b_schemas
from tgbot.services.bitrix.bitrix import create_contact


async def create_rub_thb_deal(bitrix: BitrixAsync, deal_data: b_schemas.RubThbDeal) -> int:
    cf_prefix = 'UF_CRM_'

    contact_id = await create_contact(bitrix, {'customer_name': deal_data.customer_name,
                                               'phone_number': deal_data.phone_number,
                                               'telegram_id': deal_data.telegram_id})

    return await bitrix.call('crm.deal.add', {'fields': {
        'TITLE': f'{deal_data.customer_name} {deal_data.phone_number if deal_data.phone_number else "нет номера"}',
        'CONTACT_ID': contact_id,
        'OPPORTUNITY': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_TYPE': deal_data.exchange_type,
        f'{cf_prefix}DEAL_TYPE': deal_data.deal_type,
        f'{cf_prefix}CUSTOMER_RECEIVE': deal_data.customer_receive,
        f'{cf_prefix}CUSTOMER_GIVE': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_RATE': deal_data.exchange_rate,
        f'{cf_prefix}SENDING_BANK': deal_data.rub_bank,
        f'{cf_prefix}RECEIVE_BANK': deal_data.thb_bank,
        f'{cf_prefix}RECEIVE_BANK_REQUISITES': deal_data.thb_bank_requisites,
    }})


async def create_usdt_thb_deal(bitrix: BitrixAsync, deal_data: b_schemas.UsdtThbDeal) -> int:
    cf_prefix = 'UF_CRM_'

    contact_id = await create_contact(bitrix, {'customer_name': deal_data.customer_name,
                                               'phone_number': deal_data.phone_number,
                                               'telegram_id': deal_data.telegram_id})

    return await bitrix.call('crm.deal.add', {'fields': {
        'TITLE': f'{deal_data.customer_name} {deal_data.phone_number if deal_data.phone_number else "нет номера"}',
        'CONTACT_ID': contact_id,
        'OPPORTUNITY': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_TYPE': deal_data.exchange_type,
        f'{cf_prefix}DEAL_TYPE': deal_data.deal_type,
        f'{cf_prefix}CUSTOMER_RECEIVE': deal_data.customer_receive,
        f'{cf_prefix}CUSTOMER_GIVE': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_RATE': deal_data.exchange_rate,
        f'{cf_prefix}USDT_NETWORK': deal_data.usdt_network,
        f'{cf_prefix}USDT_REQUISITES': deal_data.usdt_requisites,
        f'{cf_prefix}RECEIVE_BANK': deal_data.thai_bank,
        f'{cf_prefix}RECEIVE_BANK_REQUISITES': deal_data.thai_bank_requisites,
    }})


async def create_thb_rub_deal(bitrix: BitrixAsync, deal_data: b_schemas.ThbRubDeal) -> int:
    cf_prefix = 'UF_CRM_'

    contact_id = await create_contact(bitrix, {'customer_name': deal_data.customer_name,
                                               'phone_number': deal_data.phone_number,
                                               'telegram_id': deal_data.telegram_id})

    return await bitrix.call('crm.deal.add', {'fields': {
        'TITLE': f'{deal_data.customer_name} {deal_data.phone_number if deal_data.phone_number else "нет номера"}',
        'CONTACT_ID': contact_id,
        'OPPORTUNITY': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_TYPE': deal_data.exchange_type,
        f'{cf_prefix}DEAL_TYPE': deal_data.deal_type,
        f'{cf_prefix}CUSTOMER_RECEIVE': deal_data.customer_receive,
        f'{cf_prefix}CUSTOMER_GIVE': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_RATE': deal_data.exchange_rate,
        f'{cf_prefix}SENDING_BANK': deal_data.thb_bank,
        f'{cf_prefix}RECEIVE_BANK': deal_data.ru_bank,
        f'{cf_prefix}RECEIVE_BANK_REQUISITES': deal_data.ru_bank_requisites,
    }})


async def create_thb_usdt_deal(bitrix: BitrixAsync, deal_data: b_schemas.ThbUsdtDeal) -> int:
    cf_prefix = 'UF_CRM_'

    contact_id = await create_contact(bitrix, {'customer_name': deal_data.customer_name,
                                               'phone_number': deal_data.phone_number,
                                               'telegram_id': deal_data.telegram_id})

    return await bitrix.call('crm.deal.add', {'fields': {
        'TITLE': f'{deal_data.customer_name} {deal_data.phone_number if deal_data.phone_number else "нет номера"}',
        'CONTACT_ID': contact_id,
        'OPPORTUNITY': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_TYPE': deal_data.exchange_type,
        f'{cf_prefix}DEAL_TYPE': deal_data.deal_type,
        f'{cf_prefix}CUSTOMER_RECEIVE': deal_data.customer_receive,
        f'{cf_prefix}CUSTOMER_GIVE': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_RATE': deal_data.exchange_rate,
        f'{cf_prefix}RECEIVE_BANK': deal_data.thb_bank,
        f'{cf_prefix}USDT_NETWORK': deal_data.usdt_network,
        f'{cf_prefix}USDT_REQUISITES': deal_data.usdt_requisites,
    }})


async def create_usdt_rub_deal(bitrix: BitrixAsync, deal_data: b_schemas.UsdtRubDeal) -> int:
    cf_prefix = 'UF_CRM_'

    contact_id = await create_contact(bitrix, {'customer_name': deal_data.customer_name,
                                               'phone_number': deal_data.phone_number,
                                               'telegram_id': deal_data.telegram_id})

    return await bitrix.call('crm.deal.add', {'fields': {
        'TITLE': f'{deal_data.customer_name} {deal_data.phone_number if deal_data.phone_number else "нет номера"}',
        'CONTACT_ID': contact_id,
        'OPPORTUNITY': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_TYPE': deal_data.exchange_type,
        f'{cf_prefix}DEAL_TYPE': deal_data.deal_type,
        f'{cf_prefix}CUSTOMER_RECEIVE': deal_data.customer_receive,
        f'{cf_prefix}CUSTOMER_GIVE': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_RATE': deal_data.exchange_rate,
        f'{cf_prefix}RECEIVE_BANK': deal_data.rub_bank,
        f'{cf_prefix}RECEIVE_BANK_REQUISITES': deal_data.rub_bank_requisites,
    }})


async def create_cash_rub_thb_deal(bitrix: BitrixAsync, deal_data: b_schemas.CashRubThbDeal) -> int:
    cf_prefix = 'UF_CRM_'

    contact_id = await create_contact(bitrix, {'customer_name': deal_data.customer_name,
                                               'phone_number': deal_data.phone_number,
                                               'telegram_id': deal_data.telegram_id})

    return await bitrix.call('crm.deal.add', {'fields': {
        'TITLE': f'{deal_data.customer_name} {deal_data.phone_number if deal_data.phone_number else "нет номера"}',
        'CONTACT_ID': contact_id,
        'OPPORTUNITY': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_TYPE': deal_data.exchange_type,
        f'{cf_prefix}DEAL_TYPE': deal_data.deal_type,
        f'{cf_prefix}CUSTOMER_RECEIVE': deal_data.customer_receive,
        f'{cf_prefix}CUSTOMER_GIVE': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_RATE': deal_data.exchange_rate,
        f'{cf_prefix}LOCATION': deal_data.location,
        f'{cf_prefix}SENDING_BANK': deal_data.ru_bank,
        f'{cf_prefix}LOCATION_COMMENT': deal_data.location_comment,
    }})


async def create_cash_usdt_thb_deal(bitrix: BitrixAsync, deal_data: b_schemas.CashUsdtThbDeal) -> int:
    cf_prefix = 'UF_CRM_'

    contact_id = await create_contact(bitrix, {'customer_name': deal_data.customer_name,
                                               'phone_number': deal_data.phone_number,
                                               'telegram_id': deal_data.telegram_id})

    return await bitrix.call('crm.deal.add', {'fields': {
        'TITLE': f'{deal_data.customer_name} {deal_data.phone_number if deal_data.phone_number else "нет номера"}',
        'CONTACT_ID': contact_id,
        'OPPORTUNITY': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_TYPE': deal_data.exchange_type,
        f'{cf_prefix}DEAL_TYPE': deal_data.deal_type,
        f'{cf_prefix}CUSTOMER_RECEIVE': deal_data.customer_receive,
        f'{cf_prefix}CUSTOMER_GIVE': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_RATE': deal_data.exchange_rate,
        f'{cf_prefix}LOCATION': deal_data.location,
        f'{cf_prefix}USDT_NETWORK': deal_data.usdt_network,
        f'{cf_prefix}LOCATION_COMMENT': deal_data.location_comment,
    }})


async def create_cash_thb_rub_deal(bitrix: BitrixAsync, deal_data: b_schemas.CashThbRubDeal) -> int:
    cf_prefix = 'UF_CRM_'

    contact_id = await create_contact(bitrix, {'customer_name': deal_data.customer_name,
                                               'phone_number': deal_data.phone_number,
                                               'telegram_id': deal_data.telegram_id})

    return await bitrix.call('crm.deal.add', {'fields': {
        'TITLE': f'{deal_data.customer_name} {deal_data.phone_number if deal_data.phone_number else "нет номера"}',
        'CONTACT_ID': contact_id,
        'OPPORTUNITY': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_TYPE': deal_data.exchange_type,
        f'{cf_prefix}DEAL_TYPE': deal_data.deal_type,
        f'{cf_prefix}CUSTOMER_RECEIVE': deal_data.customer_receive,
        f'{cf_prefix}CUSTOMER_GIVE': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_RATE': deal_data.exchange_rate,
        f'{cf_prefix}LOCATION': deal_data.location,
        f'{cf_prefix}RECEIVE_BANK': deal_data.ru_bank,
        f'{cf_prefix}RECEIVE_BANK_REQUISITES': deal_data.ru_bank_requisites,
        f'{cf_prefix}LOCATION_COMMENT': deal_data.location_comment,
    }})


async def create_cash_thb_usdt_deal(bitrix: BitrixAsync, deal_data: b_schemas.CashThbUsdtDeal) -> int:
    cf_prefix = 'UF_CRM_'

    contact_id = await create_contact(bitrix, {'customer_name': deal_data.customer_name,
                                               'phone_number': deal_data.phone_number,
                                               'telegram_id': deal_data.telegram_id})

    return await bitrix.call('crm.deal.add', {'fields': {
        'TITLE': f'{deal_data.customer_name} {deal_data.phone_number if deal_data.phone_number else "нет номера"}',
        'CONTACT_ID': contact_id,
        'OPPORTUNITY': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_TYPE': deal_data.exchange_type,
        f'{cf_prefix}DEAL_TYPE': deal_data.deal_type,
        f'{cf_prefix}CUSTOMER_RECEIVE': deal_data.customer_receive,
        f'{cf_prefix}CUSTOMER_GIVE': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_RATE': deal_data.exchange_rate,
        f'{cf_prefix}LOCATION': deal_data.location,
        f'{cf_prefix}USDT_NETWORK': deal_data.usdt_network,
        f'{cf_prefix}USDT_REQUISITES': deal_data.usdt_requisites,
        f'{cf_prefix}LOCATION_COMMENT': deal_data.location_comment,
    }})


async def create_usdt_dividends_deal(bitrix: BitrixAsync, deal_data: b_schemas.UsdtDividendsDeal) -> int:
    cf_prefix = 'UF_CRM_'

    contact_id = await create_contact(bitrix, {'customer_name': deal_data.customer_name,
                                               'phone_number': deal_data.phone_number,
                                               'telegram_id': deal_data.telegram_id})
    return await bitrix.call('crm.deal.add', {'fields': {
        'TITLE': f'{deal_data.customer_name} {deal_data.phone_number if deal_data.phone_number else "нет номера"}',
        'CONTACT_ID': contact_id,
        'OPPORTUNITY': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_TYPE': deal_data.exchange_type,
        f'{cf_prefix}DEAL_TYPE': deal_data.deal_type,
        f'{cf_prefix}CUSTOMER_RECEIVE': deal_data.customer_receive,
        f'{cf_prefix}CUSTOMER_GIVE': deal_data.customer_give,
        f'{cf_prefix}EXCHANGE_RATE': deal_data.exchange_rate,
        f'{cf_prefix}USDT_NETWORK': deal_data.usdt_network,
        f'{cf_prefix}USDT_REQUISITES': deal_data.usdt_requisites,
    }})
