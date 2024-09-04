from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.keyboards import reply_keyboards
from tgbot.misc import states, callbacks


async def start_token_input(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.answer('Введите реквизиты:', reply_markup=reply_keyboards.cancel)

    await state.update_data(token=callback_data['token'])
    await states.TokenState.waiting_for_token.set()
    await call.answer()


async def get_token(message: Message, state: FSMContext):
    wallet = message.text.strip()

    async with state.proxy() as data:
        token = data['token']
    await message.answer('Введите сумму для вывода:', reply_markup=reply_keyboards.cancel)
    await states.WithdrawalState.waiting_for_sum.set()
    await state.update_data(token=token, wallet=wallet, type='rub')


def register_token(dp: Dispatcher):
    dp.register_callback_query_handler(start_token_input, callbacks.token_choose.filter())
    dp.register_message_handler(get_token, state=states.TokenState.waiting_for_token)
