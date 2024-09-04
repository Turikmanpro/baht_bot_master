import datetime

from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import tgbot.keyboards.inline_permutations_keyboards as inline_keyboards
from tgbot.handlers.admin import show_admin_menu
from tgbot.misc import messages, callbacks
from tgbot.services.database.models import User, Referral, Mover, MoverOrder


async def show_movers_menu(call: CallbackQuery):
    await call.message.edit_text('Перестановищики', reply_markup=inline_keyboards.mover_menu)
    await call.answer()


async def add_mover_menu(call: CallbackQuery):
    async_session: AsyncSession = call.bot.get('database')
    async with async_session.begin() as session:
        records = await session.execute(select(Referral).where(Referral.is_original == True))
        oringinal_referrals = records.scalars().all()
        orig_ref_ids = [int(i.id) for i in oringinal_referrals]
    await call.message.edit_text('Добавить перестановщика',
                                 reply_markup=inline_keyboards.get_mover_orig_referral_keyboard(orig_ref_ids))
    await call.answer()


async def add_mover_user_list(call: CallbackQuery, callback_data: dict):
    orig_ref_id = int(callback_data['id'])
    page = int(callback_data['page'])
    async_session: AsyncSession = call.bot.get('database')
    config = call.bot.get('config')
    async with async_session.begin() as session:
        referrals = await session.execute(
            select(Referral).where(Referral.original_referral_id == orig_ref_id, Referral.is_original == False))
        referrals = referrals.scalars().all()
        referrals = [{'id': i.user.telegram_id, 'name': i.user.name, 'orig_ref_id': orig_ref_id} for i in referrals]
    if orig_ref_id == 0:
        orig_ref_id = ' Дефолтный'
    await call.message.edit_text(f'Рефералы ИР{orig_ref_id}',
                                 reply_markup=inline_keyboards.get_mover_ref_list_keyboard(referrals,
                                                                                           config.misc.items_per_page,
                                                                                           page, 'add'))
    await call.answer()


async def update_mover(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    telegram_id = int(callback_data['payload'])
    async with async_session.begin() as session:
        mover = await session.get(Mover, telegram_id)
        if mover:
            mover.deleted = not mover.deleted
        else:
            mover = Mover(telegram_id=telegram_id)
            session.add(mover)
    await call.answer('Успешно!', show_alert=True)
    await show_admin_menu(call)


async def take_mover_order(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')
    mover_order_id = int(callback_data['order_id'])
    async with async_session.begin() as session:
        print(mover_order_id)
        order = await session.get(MoverOrder, mover_order_id)

        if order.mover:
            await call.answer('Заказ уже обрабатывает другой оператор!', show_alert=True)
            return

        order.mover_id = call.from_user.id
        order.answered_at = datetime.datetime.now()
        await call.answer('Вы назначены на этот заказ!', show_alert=True)


def register_movers_add(dp: Dispatcher):
    dp.register_callback_query_handler(show_movers_menu, callbacks.navigation.filter(to='movers'))
    dp.register_callback_query_handler(add_mover_menu, callbacks.movers.filter(to='add_menu'))
    dp.register_callback_query_handler(add_mover_user_list, callbacks.movers_orig_ref_choose.filter())
    dp.register_callback_query_handler(update_mover, callbacks.movers.filter(to='update_mover'))
    dp.register_callback_query_handler(take_mover_order, callbacks.movers_order.filter(action='take'))
