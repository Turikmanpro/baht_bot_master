from decimal import ROUND_HALF_DOWN, Decimal

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import select

from tgbot.keyboards.inline_exchange_keyboards import exchange_start_menu
from tgbot.misc import callbacks, messages, states
from tgbot.services import AsyncBinance
from tgbot.keyboards import inline_keyboards, reply_keyboards
from tgbot.services.database.models import User, Referral


async def show_main_menu(call: CallbackQuery, state: FSMContext):
    await state.finish()
    db_session = call.bot.get('database')
    async with db_session() as session:
        user = await session.get(User, call.from_user.id)
        keyboard = reply_keyboards.get_main_keyboard(show_reg_button=not user.is_reg, is_courier=user.courier)
        await call.message.answer(messages.main_menu, reply_markup=keyboard)
    await call.answer()


async def show_exchange_rate(call: CallbackQuery):
    config = call.bot.get('config')

    usdt_avg_price = await AsyncBinance.get_avg_price('RUB', 'BUY', ['TinkoffNew'])
    thb_avg_price = await AsyncBinance.get_avg_price('THB', 'SELL')

    rub_thb_price = (usdt_avg_price / thb_avg_price).quantize(Decimal('1.000'), ROUND_HALF_DOWN)

    del_coef = Decimal(1) + (Decimal(config.misc.delivery_percent) / Decimal(100))
    tran_coef = Decimal(1) + (Decimal(config.misc.transfer_percent) / Decimal(100))

    await call.message.edit_text(
        messages.exchange_rate.format(
            rt_delivery=(rub_thb_price * del_coef).quantize(Decimal('1.000'), ROUND_HALF_DOWN),
            rt_transfer=(rub_thb_price * tran_coef).quantize(Decimal('1.000'), ROUND_HALF_DOWN),
            ut_delivery=(thb_avg_price * del_coef).quantize(Decimal('1.000'), ROUND_HALF_DOWN),
            ut_transfer=(thb_avg_price * tran_coef).quantize(Decimal('1.000'), ROUND_HALF_DOWN)
        )
    )

    await call.answer()


async def show_about_us(call: CallbackQuery):
    await call.message.edit_text(messages.about)
    await call.answer()


async def show_referral_menu(call: CallbackQuery):
    config = call.bot.get('config')
    await call.message.delete()
    await call.message.answer_video(config.videos_id.earn_usdt, caption=messages.referral_menu,
                                    reply_markup=inline_keyboards.referral_menu)
    # await call.message.edit_text(messages.referral_menu, reply_markup=inline_keyboards.referral_menu)
    await call.answer()


async def show_reviews(call: CallbackQuery):
    db_session = call.bot.get('database')
    config = call.bot.get('config')

    async with db_session() as session:
        user = await session.get(User, call.from_user.id)
        # TODO: get value below from db
        is_completed_deal = True

    is_admin = call.from_user.id in config.tg_bot.admin_ids

    await call.message.edit_text(messages.reviews,
                                 reply_markup=inline_keyboards.get_reviews_keyboard(is_admin, is_completed_deal))
    await call.answer()


async def show_exchange_menu(call: CallbackQuery, state: FSMContext):
    db_session = call.bot.get('database')
    await state.finish()
    async with db_session() as session:
        user = await session.get(User, call.from_user.id)
        if not user.is_reg:
            await call.answer('В целях безопасности, пожалуйста зарегистрируйтесь для совершения обмена',
                              show_alert=True)
            return
        referral = await session.execute(select(Referral).where(Referral.telegram_id == call.from_user.id))
        referral = (referral.scalars().all())[0]
        if referral.is_blocked:
            await call.answer('Ваш аккаунт заблокирован. У вас нет доступа к обмену', show_alert=True)
            return
    await call.message.delete()
    await call.message.answer(messages.exchange_menu, reply_markup=exchange_start_menu)
    await call.answer()


async def start_registration(call: CallbackQuery, state: FSMContext):
    msg = await call.message.answer(messages.email_request, reply_markup=reply_keyboards.cancel)

    await state.update_data(main_msg_id=msg.message_id)
    await states.RegistrationState.waiting_for_email.set()
    await call.answer()


def register_main_menu(dp: Dispatcher):
    dp.register_callback_query_handler(show_main_menu, callbacks.navigation.filter(to='main_menu'), state='*')
    dp.register_callback_query_handler(show_exchange_rate, callbacks.navigation.filter(to='ex_rate'))
    dp.register_callback_query_handler(show_about_us, callbacks.navigation.filter(to='about'))
    dp.register_callback_query_handler(show_referral_menu, callbacks.navigation.filter(to='ref_menu'))
    dp.register_callback_query_handler(show_reviews, callbacks.navigation.filter(to='reviews'))
    dp.register_callback_query_handler(show_exchange_menu, callbacks.navigation.filter(to='make_ex'), state='*')
    dp.register_callback_query_handler(start_registration, callbacks.navigation.filter(to='reg'))
