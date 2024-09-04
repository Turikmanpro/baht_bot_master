from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram.utils import markdown as md
from aiogram.utils.deep_linking import get_start_link

from tgbot.misc.helper import get_ref
from tgbot.misc import callbacks, messages
from tgbot.keyboards import inline_keyboards
from tgbot.services.database.models import User


async def show_how_it_works(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(messages.how_it_works, reply_markup=inline_keyboards.get_back_keyboard('ref_menu'))
    await call.answer()


async def show_ref_link(call: CallbackQuery):
    db_session = call.bot.get('database')
    async with db_session() as session:
        user = await session.get(User, call.from_user.id)
        if not user.is_reg:
            await call.answer('Для получения ссылки нужно зарегистрироваться!', show_alert=True)
            return

    ref_link = await get_start_link(call.from_user.id, encode=True)
    await call.message.delete()
    await call.message.answer(messages.referral_link.format(link=md.hcode(ref_link)),
                                 reply_markup=inline_keyboards.get_back_keyboard('ref_menu'))
    await call.answer()


async def show_stats_menu(call: CallbackQuery):
    db_session = call.bot.get('database')
    async with db_session() as session:
        user = await session.get(User, call.from_user.id)
        referral = await get_ref(session, call.from_user.id)

        exchanges_count = referral.ref_deals_count
        dividends_05 = round(referral.lvl1_ref_balance)
        dividends_03 = round(referral.lvl2_ref_balance)
        dividends_02 = round(referral.lvl3_ref_balance)
        dividends_sum = round(referral.ref_balance)
    await call.message.delete()
    await call.message.answer(
        messages.stats.format(
            exchanges_count=exchanges_count,
            dividends_05=dividends_05,
            dividends_03=dividends_03,
            dividends_02=dividends_02,
            dividends_sum=dividends_sum
        ),
        reply_markup=inline_keyboards.statistics_menu
    )
    await call.answer()


async def show_ref_withdrawal_menu(call: CallbackQuery):
    await call.message.edit_text('Вывести дивиденды', reply_markup=inline_keyboards.referral_withdrawal_menu)
    await call.answer()


def register_referral(dp: Dispatcher):
    dp.register_callback_query_handler(show_how_it_works, callbacks.navigation.filter(to='how_works'))
    dp.register_callback_query_handler(show_ref_link, callbacks.navigation.filter(to='ref_link'))
    dp.register_callback_query_handler(show_stats_menu, callbacks.navigation.filter(to='stats'))
    dp.register_callback_query_handler(show_ref_withdrawal_menu, callbacks.navigation.filter(to='ref_withdrawal_menu'))
