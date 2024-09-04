from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.keyboards import reply_keyboards
from tgbot.misc import states, callbacks


async def start_card_number_input(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.answer('Введите номер вашей карты:', reply_markup=reply_keyboards.cancel)

    await state.update_data(bank=callback_data['bank'])
    await states.CardNumberState.waiting_for_number.set()
    await call.answer()


async def get_card_number(message: Message, state: FSMContext):
    card_number = message.text.replace('-', '').replace(' ', '')
    if len(card_number) != 16 or not card_number.isdigit():
        await message.answer('Неверный номер карты. Попробуйте ещё раз:')
        return

    async with state.proxy() as data:
        bank = data['bank']
    await message.answer('Введите сумму для вывода:', reply_markup=reply_keyboards.cancel)
    await states.WithdrawalState.waiting_for_sum.set()
    await state.update_data(card=card_number, bank=bank, type='rub')


def register_bank(dp: Dispatcher):
    dp.register_callback_query_handler(start_card_number_input, callbacks.bank_choose.filter(type='withdraw'))
    dp.register_message_handler(get_card_number, state=states.CardNumberState.waiting_for_number)
