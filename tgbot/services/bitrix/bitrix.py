import asyncio
import base64
import datetime

from fast_bitrix24 import BitrixAsync

from tgbot.services.bitrix.bitrix_schemas import SellStage, ExchangeType, DealType
from tgbot.services.database.models import Order


async def change_deal_stage(bitrix: BitrixAsync, stage: str, deal_id: int) -> None:
    await bitrix.call('crm.deal.update', {'id': deal_id, 'fields': {'STAGE_ID': stage}})


async def create_contact(bitrix: BitrixAsync, contact_data: dict) -> int:
    contact = {
        'NAME': contact_data['customer_name'],
        'OPENED': 'Y',
        'TYPE_ID': 'CLIENT',
        'PHONE': [{'VALUE': contact_data['phone_number'], 'VALUE_TYPE': 'WORK'}],
        'UF_CRM_TELEGRAM_ID': contact_data['telegram_id']
    }
    return await bitrix.call('crm.contact.add', {'fields': contact})


async def get_contact(bitrix: BitrixAsync, contact_id: int) -> dict:
    return await bitrix.call('crm.contact.get', {'id': contact_id})


async def add_courier(bitrix: BitrixAsync, telegram_id: int, name: str) -> int:
    return await bitrix.call('crm.product.add', {'fields': {
        'NAME': name,
        'CURRENCY_ID': 'RUB',
        'PRICE': 0,
        'DESCRIPTION': telegram_id,
        'CATALOG_ID': 77
    }})


async def remove_courier(bitrix: BitrixAsync, product_id: int) -> None:
    await bitrix.call('crm.product.delete', {'id': product_id})


async def get_couriers_for_delivery(bitrix: BitrixAsync):
    deals = await bitrix.get_all('crm.deal.list', {
        'filter': {'STAGE_ID': SellStage.COURIER_CHOICE},
        'select': ['*', 'UF_*']
    })

    couriers = []
    for deal in deals:
        try:
            product_data = await bitrix.call('crm.deal.productrows.get', {
                'id': deal['ID']
            })
            await asyncio.sleep(0.7)
            couriers.append({'deal_id': deal['ID'], 'courier_id': product_data['PRODUCT_DESCRIPTION']})
        except Exception as e:
            pass

    return couriers


async def change_courier_availability(bitrix: BitrixAsync, product_id: int, name: str, is_working: bool):
    if is_working:
        name += ' (Занят)'
    await bitrix.call('crm.product.update', {
        'id': product_id,
        'fields': {'NAME': name}
    })


async def send_file(bitrix: BitrixAsync, order_id: int, path: str):
    with open(path, 'rb') as f:
        a = base64.b64encode(f.read())
    await bitrix.call('crm.deal.update', {
        'id': order_id,
        'fields': {
            'UF_CRM_PAYMENT_FILE': {
                'fileData': ['test.pdf', a]
            }
        }
    })


async def update_deal_sum(bitrix: BitrixAsync, order_id, ex_rate, customer_give, customer_receive):
    cf_prefix = 'UF_CRM_'
    await bitrix.call('crm.deal.update', {
        'id': order_id,
        'fields': {
            f'{cf_prefix}CUSTOMER_RECEIVE': customer_receive,
            f'{cf_prefix}CUSTOMER_GIVE': customer_give,
            f'{cf_prefix}EXCHANGE_RATE': ex_rate,
        }
    })


async def send_email(bitrix: BitrixAsync, customer_email, message, contact_id=24, staff_id=1,
                     bot_email='bahtbot429@gmail.com'):
    await bitrix.call('crm.activity.add', {'fields': {
        'SUBJECT': 'Verify your email',
        'DESCRIPTION': message,
        'DESCRIPTION_TYPE': '3',
        'COMPLETED': 'Y',
        'DIRECTION': '2',
        'OWNER_ID': contact_id,  # contact id
        'OWNER_TYPE_ID': '3',
        'TYPE_ID': '4',
        'COMMUNICATIONS': [
            {'VALUE': customer_email, 'ENTITY_ID': contact_id, 'ENTITY_TYPE_ID': '3'}  # contact id
        ],
        'START_TIME': datetime.datetime.now(),
        'END_TIME': datetime.datetime.now() + datetime.timedelta(seconds=3600),
        'RESPONSIBLE_ID': staff_id,  # my_id
        'SETTINGS': {
            'MESSAGE_FROM': f'BAHT BOT <{bot_email}>'
        }

    }})
