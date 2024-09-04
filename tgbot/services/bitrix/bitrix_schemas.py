from dataclasses import dataclass


class ExchangeType(str):
    RUB_THB = 'RUB/THB'
    USDT_THB = 'USDT/THB'
    THB_RUB = 'THB/RUB'
    THB_USDT = 'THB/USDT'
    USDT_RUB = 'USDT/RUB'
    RUB_USDT = 'RUB/USDT'
    USDT_USDT = 'USDT/USDT'


class DealType(str):
    CASH = 'Наличные'
    COURIER = 'Доставка курьером'
    THAI_TRANSFER = 'Перевод на тайский счет'
    RUS_TRANSFER = 'Перевод на русский счет'
    QUICK_DEAL = 'Быстрая сделка'
    OFTEN_DEAL = 'Обычная сделка'
    DIVIDENDS_RUB = 'Дивиденды: RUB'
    DIVIDENDS_USDT = 'Дивиденды: USDT'
    DIVIDENDS_THB = 'Дивиденды: THB'


class SellStage(str):
    REQUEST = 'NEW'
    COURIER_CHOICE = 'PREPARATION'
    WAITING_FOR_DELIVERY = 'PREPAYMENT_INVOICE'
    DELIVERY = 'EXECUTING'
    PROBLEM = 'FINAL_INVOICE'
    EXCHANGE = 'UC_PV00K7'
    FINISHED = 'UC_HG0ZAG'
    REMOVE_FINISHED = 'WON'
    CANCELED = 'UC_N7JEGQ'


@dataclass
class Deal:
    exchange_type: ExchangeType
    deal_type: DealType
    customer_name: str
    telegram_id: int
    phone_number: str
    customer_receive: float
    customer_give: float
    exchange_rate: float


@dataclass
class CashDeal(Deal):
    location: str
    location_comment: str


# Cash deal types
@dataclass
class CashRubThbDeal(CashDeal):
    ru_bank: str


@dataclass
class CashUsdtThbDeal(CashDeal):  
    usdt_network: str


@dataclass
class CashThbRubDeal(CashDeal):
    ru_bank: str
    ru_bank_requisites: str


@dataclass
class CashThbUsdtDeal(CashDeal):
    usdt_network: str
    usdt_requisites: str  # send usdt here to user


# Non-cash deal types
@dataclass
class RubThbDeal(Deal):
    rub_bank: str
    thb_bank: str
    thb_bank_requisites: str


@dataclass
class UsdtThbDeal(Deal):
    usdt_network: str
    usdt_requisites: str
    thai_bank: str  # Реквизиты для получения THB
    thai_bank_requisites: str


@dataclass
class ThbRubDeal(Deal):
    ru_bank: str  # Получаем RUB
    ru_bank_requisites: str
    thb_bank: str


@dataclass
class ThbUsdtDeal(Deal):
    thb_bank: str
    usdt_network: str
    usdt_requisites: str


@dataclass
class UsdtRubDeal(Deal):  # Для вывода от реферала
    rub_bank: str
    rub_bank_requisites: str


@dataclass
class UsdtDividendsDeal(Deal):  # Для вывода от реферала
    usdt_network: str
    usdt_requisites: str

