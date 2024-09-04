from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ContentTypes, InputMediaVideo

from tgbot.misc import states, callbacks, messages
from tgbot.keyboards.inline_exchange_keyboards import *
from tgbot.services.bitrix.bitrix_schemas import DealType


async def show_choose_payment_way_menu(call: CallbackQuery, callback_data: dict):
    client_want = callback_data['payload']
    await call.message.edit_text('Тип выдачи?', reply_markup=get_choose_payment_way_menu(client_want))
    await call.answer()


async def show_choose_currency_non_cash_menu(call: CallbackQuery, callback_data: dict):
    config = call.bot.get('config')
    client_want = callback_data['payload']
    await call.message.delete()
    if client_want == 'sell_thb':
        await call.message.answer_video(config.videos_id.non_cash_back, caption='Валюта', reply_markup=get_choose_currency_sell_menu([DealType.RUS_TRANSFER, DealType.THAI_TRANSFER]))
        # await call.message.edit_text('Валюта', reply_markup=get_choose_currency_sell_menu([DealType.RUS_TRANSFER, DealType.THAI_TRANSFER]))
    elif client_want == 'buy_thb':
        await call.message.answer_video(config.videos_id.non_cash, caption='Валюта',
                                        reply_markup=get_choose_currency_buy_menu(
                                            [DealType.THAI_TRANSFER, DealType.THAI_TRANSFER]))
        # await call.message.edit_text('Валюта', reply_markup=get_choose_currency_buy_menu(
        #     [DealType.THAI_TRANSFER, DealType.THAI_TRANSFER]))
    await call.answer()


async def show_choose_currency_cash_menu(call: CallbackQuery, callback_data: dict):
    config = call.bot.get('config')
    client_want = callback_data['payload']
    if client_want == 'sell_thb':
        await call.answer('Функционал в разработке', show_alert=True)
        return
        # await call.message.edit_text('Валюта', reply_markup=get_choose_currency_sell_menu(
        #     [DealType.CASH, DealType.CASH]))
    elif client_want == 'buy_thb':
        await call.message.delete()
        await call.message.answer_video(config.videos_id.courier, caption='Валюта',
                                        reply_markup=get_choose_currency_buy_menu(
                                            [DealType.CASH, DealType.COURIER]))
        # await call.message.edit_text('Валюта', reply_markup=get_choose_currency_buy_menu(
        #     [DealType.CASH, DealType.COURIER]))
    await call.answer()


def register_pre_deal(dp: Dispatcher):
    dp.register_callback_query_handler(show_choose_payment_way_menu, callbacks.navigation.filter(to='exchange'))
    dp.register_callback_query_handler(show_choose_currency_non_cash_menu, callbacks.navigation.filter(to='non_cash_ex'))
    dp.register_callback_query_handler(show_choose_currency_cash_menu, callbacks.navigation.filter(to='cash_ex'))

