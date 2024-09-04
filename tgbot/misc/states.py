from aiogram.dispatcher.filters.state import StatesGroup, State


class RegistrationState(StatesGroup):
    waiting_for_email = State()
    waiting_for_email_confirm_code = State()
    waiting_for_phone = State()


class CardNumberState(StatesGroup):
    waiting_for_number = State()


class TokenState(StatesGroup):
    waiting_for_token = State()


class ExchangeState(StatesGroup):
    waiting_for_exchange_currencies = State()
    waiting_for_delivery_type = State()


class OrderUpdateState(StatesGroup):
    waiting_for_value = State()


class WithdrawalState(StatesGroup):
    waiting_for_sum = State()


class ExchangeAmountState(StatesGroup):
    waiting_for_sum = State()
    waiting_for_data = State()
    waiting_for_location = State()
    waiting_for_location_comment = State()
    waiting_for_crm = State()
    waiting_for_requisites = State()


class SettingsState(StatesGroup):
    waiting_for_percent = State()


class ClientChange(StatesGroup):
    waiting_for_sum = State()


class OperatorOrderState(StatesGroup):
    waiting_for_requisites = State()


class CustomerOrderState(StatesGroup):
    waiting_for_scan = State()


class QuickDeal(StatesGroup):
    waiting_for_acceptance_city = State()
    waiting_for_currency = State()
    waiting_for_type = State()
    waiting_for_sum = State()
    waiting_for_country = State()
    waiting_for_confirm = State()


class OftenMoversDeal(StatesGroup):
    waiting_for_currency = State()
    waiting_for_receiving_office = State()
    waiting_for_type = State()
    waiting_for_sum = State()
    waiting_for_country = State()
    waiting_for_city = State()
    waiting_for_confirm = State()
