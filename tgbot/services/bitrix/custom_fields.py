import asyncio
from fast_bitrix24 import BitrixAsync


async def create_custom_fields(bitrix: BitrixAsync) -> None:
    # add custom deal fields
    custom_deal_fields = [
        {
            'FIELD_NAME': 'exchange_type',
            'EDIT_FORM_LABEL': 'Тип обмена',
            'LIST_COLUMN_LABEL': 'Тип обмена',
            'USER_TYPE_ID': 'string',
            'MANDATORY': 'Y'
        },
        {
            'FIELD_NAME': 'deal_type',
            'EDIT_FORM_LABEL': 'Вид сделки',
            'LIST_COLUMN_LABEL': 'Вид сделки',
            'USER_TYPE_ID': 'string',
            'MANDATORY': 'Y'
        },
        {
            'FIELD_NAME': 'customer_receive',
            'EDIT_FORM_LABEL': 'Сумма к выдаче',
            'LIST_COLUMN_LABEL': 'Сумма к выдаче',
            'USER_TYPE_ID': 'string',
            'MANDATORY': 'Y'
        },
        {
            'FIELD_NAME': 'customer_give',
            'EDIT_FORM_LABEL': 'Сумма к обмену',
            'LIST_COLUMN_LABEL': 'Сумма к обмену',
            'USER_TYPE_ID': 'string',
            'MANDATORY': 'Y'
        },
        {
            'FIELD_NAME': 'exchange_rate',
            'EDIT_FORM_LABEL': 'Курс',
            'LIST_COLUMN_LABEL': 'Курс',
            'USER_TYPE_ID': 'string',
            'MANDATORY': 'Y'
        },
        {
            'FIELD_NAME': 'sending_bank',
            'EDIT_FORM_LABEL': 'Банк отправитель',
            'LIST_COLUMN_LABEL': 'Банк отправитель',
            'USER_TYPE_ID': 'string',
        },
        {
            'FIELD_NAME': 'sending_bank_requisites',
            'EDIT_FORM_LABEL': 'Реквизиты банка отправителя',
            'LIST_COLUMN_LABEL': 'Реквизиты банка отправителя',
            'USER_TYPE_ID': 'string',
        },
        {
            'FIELD_NAME': 'receive_bank',
            'EDIT_FORM_LABEL': 'Банк получатель',
            'LIST_COLUMN_LABEL': 'Банк получатель',
            'USER_TYPE_ID': 'string',
        },
        {
            'FIELD_NAME': 'receive_bank_requisites',
            'EDIT_FORM_LABEL': 'Реквизиты банка получателя',
            'LIST_COLUMN_LABEL': 'Реквизиты банка получателя',
            'USER_TYPE_ID': 'string',
        },
        {
            'FIELD_NAME': 'location',
            'EDIT_FORM_LABEL': 'Локация',
            'LIST_COLUMN_LABEL': 'Локация',
            'USER_TYPE_ID': 'string',
        },
        {
            'FIELD_NAME': 'usdt_network',
            'EDIT_FORM_LABEL': 'Сеть USDT',
            'LIST_COLUMN_LABEL': 'Сеть USDT',
            'USER_TYPE_ID': 'string',
        },
        {
            'FIELD_NAME': 'usdt_requisites',
            'EDIT_FORM_LABEL': 'Реквизиты USDT',
            'LIST_COLUMN_LABEL': 'Реквизиты USDT',
            'USER_TYPE_ID': 'string',
        },
        {
            'FIELD_NAME': 'location_comment',
            'EDIT_FORM_LABEL': 'Комментарий',
            'LIST_COLUMN_LABEL': 'Комментарий',
            'USER_TYPE_ID': 'string',
        },
        {
            'FIELD_NAME': 'payment_file',
            'EDIT_FORM_LABEL': 'Файл',
            'LIST_COLUMN_LABEL': 'Файл',
            'USER_TYPE_ID': 'file',
        },
    ]

    for field in custom_deal_fields:
        await bitrix.call('crm.deal.userfield.add', {'fields': field})

    custom_client_fields = [
        {
            'FIELD_NAME': 'telegram_id',
            'EDIT_FORM_LABEL': 'Telegram ID',
            'LIST_COLUMN_LABEL': 'Telegram ID',
            'USER_TYPE_ID': 'string',
        },
    ]
    for field in custom_client_fields:
        await bitrix.call('crm.contact.userfield.add', {'fields': field})


async def main():
    b = BitrixAsync('webhook')

    await create_custom_fields(b)

if __name__ == '__main__':
    asyncio.run(main())


