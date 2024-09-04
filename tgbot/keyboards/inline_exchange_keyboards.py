from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.misc import callbacks
from tgbot.services.bitrix.bitrix_schemas import ExchangeType, DealType


exchange_start_menu = InlineKeyboardMarkup(row_width=1)
exchange_start_menu.add(
    InlineKeyboardButton('Купить THB', callback_data=callbacks.navigation.new(to='exchange', payload='buy_thb')),
    InlineKeyboardButton('Продать THB', callback_data=callbacks.navigation.new(to='exchange', payload='sell_thb')),
)

def get_choose_payment_way_menu(payload) -> InlineKeyboardMarkup:
    choose_payment_way_menu = InlineKeyboardMarkup(row_width=1)
    choose_payment_way_menu.add(
        InlineKeyboardButton('🏦 Перевод на Тайский Банковский счет', callback_data=callbacks.navigation.new(to='non_cash_ex', payload=payload)),
        InlineKeyboardButton('🏎 Доставка наличных курьером', callback_data=callbacks.navigation.new(to='cash_ex', payload=payload)),
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='make_ex', payload=''))
    )
    return choose_payment_way_menu

def get_choose_currency_sell_menu(deal_types: list[DealType]) -> InlineKeyboardMarkup:
    choose_currency_sell_menu = InlineKeyboardMarkup(row_width=1)
    choose_currency_sell_menu.add(
        InlineKeyboardButton('Продать THB за RUB', callback_data=callbacks.exchange.new(ex_type=ExchangeType.THB_RUB, deal_type=deal_types[0])),
        InlineKeyboardButton('Продать THB за USDT', callback_data=callbacks.exchange.new(ex_type=ExchangeType.THB_USDT, deal_type=deal_types[1])),
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='make_ex', payload=''))
    )

    return choose_currency_sell_menu

def get_choose_currency_buy_menu(deal_types: list[DealType]) -> InlineKeyboardMarkup:
    choose_currency_buy_menu = InlineKeyboardMarkup(row_width=1)
    choose_currency_buy_menu.add(
        InlineKeyboardButton('Купить THB за RUB', callback_data=callbacks.exchange.new(ex_type=ExchangeType.RUB_THB, deal_type=deal_types[0])),
        InlineKeyboardButton('Купить THB за USDT', callback_data=callbacks.exchange.new(ex_type=ExchangeType.USDT_THB, deal_type=deal_types[1])),
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='make_ex', payload=''))
    )

    return choose_currency_buy_menu

non_cash_exchange_menu = InlineKeyboardMarkup(row_width=1)
non_cash_exchange_menu.add(
    InlineKeyboardButton('Купить THB (Баты) за RUB (Рубли)', callback_data=callbacks.exchange.new(ex_type=ExchangeType.RUB_THB, deal_type=DealType.THAI_TRANSFER)),
    InlineKeyboardButton('Купить THB (Баты) за USDT', callback_data=callbacks.exchange.new(ex_type=ExchangeType.USDT_THB, deal_type=DealType.THAI_TRANSFER)),
    InlineKeyboardButton('Купить RUB (Рубли) за THB (Баты)', callback_data=callbacks.exchange.new(ex_type=ExchangeType.THB_RUB, deal_type=DealType.RUS_TRANSFER)),
    InlineKeyboardButton('Купить USDT за THB (Баты)', callback_data=callbacks.exchange.new(ex_type=ExchangeType.THB_USDT, deal_type=DealType.THAI_TRANSFER)),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='make_ex', payload=''))
)

cash_exchange_menu = InlineKeyboardMarkup(row_width=1)
cash_exchange_menu.add(
    InlineKeyboardButton('Купить наличные THB за безналичные RUB', callback_data=callbacks.exchange.new(ExchangeType.RUB_THB, DealType.CASH)),
    InlineKeyboardButton('Купить наличные THB за USDT', callback_data=callbacks.exchange.new(ExchangeType.USDT_THB, DealType.COURIER)),
    InlineKeyboardButton('Купить безналичные RUB за наличные THB', callback_data=callbacks.exchange.new(ExchangeType.THB_RUB, DealType.CASH)),
    InlineKeyboardButton('Купить USDT за наличные THB', callback_data=callbacks.exchange.new(ExchangeType.THB_USDT, DealType.CASH)),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='make_ex', payload=''))
)


def get_input_currency_menu(ex_type: ExchangeType, deal_type: DealType) -> InlineKeyboardMarkup:
    currency1, currency2 = ex_type.split('/')

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(f'Мне нужна сумма в {currency2}', callback_data=callbacks.navigation.new(to='inp_amount', payload=currency2)),
        InlineKeyboardButton(f'У меня есть сумма в {currency1}', callback_data=callbacks.navigation.new(to='inp_amount', payload=currency1)),
        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='make_ex', payload=''))
    )

    return keyboard



ex_amount_keyboard = InlineKeyboardMarkup(row_width=1)

ex_amount_keyboard.add(
    InlineKeyboardButton('Оформить заявку', callback_data=callbacks.navigation.new(to='make_deal', payload='')),
    InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='make_ex', payload=''))
)


def get_thai_bank_choose_keyboard(operation_type, back_to, payload='', back_payload=''):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('Bangkok Bank 🟦', callback_data=callbacks.bank_choose.new('Bangkok Bank', operation_type, payload)),
        InlineKeyboardButton('Kasikornbank 🟥', callback_data=callbacks.bank_choose.new('Kasikornbank', operation_type, payload)),
        InlineKeyboardButton('Siam (SCB) 🟪', callback_data=callbacks.bank_choose.new('Siam (SCB)', operation_type, payload)),
        InlineKeyboardButton('Krungsri bank 🟨', callback_data=callbacks.bank_choose.new('Krungsri bank', operation_type, payload)),

        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to=back_to, payload=back_payload))
    )

    return keyboard


def get_usdt_network_choose_keyboard(operation_type, back_to, payload='', back_payload=''):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton('TRC20', callback_data=callbacks.bank_choose.new('TRC20', operation_type, payload)),
        InlineKeyboardButton('ERC20', callback_data=callbacks.bank_choose.new('ERC20', operation_type, payload)),
        InlineKeyboardButton('BEP20', callback_data=callbacks.bank_choose.new('BEP20', operation_type, payload)),
        InlineKeyboardButton('BINANCE PAY ID', callback_data=callbacks.bank_choose.new('BINANCE PAY ID', operation_type, payload)),

        InlineKeyboardButton('Назад', callback_data=callbacks.navigation.new(to='make_ex', payload=''))
    )

    return keyboard
