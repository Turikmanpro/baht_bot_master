from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import tgbot.keyboards.inline_permutations_keyboards as inline_keyboards
from tgbot.misc import messages, callbacks
from tgbot.services.database.models import User, Mover


async def show_active_movers(call: CallbackQuery, callback_data: dict):
    page = int(callback_data['payload'])
    async_session: AsyncSession = call.bot.get('database')
    config = call.bot.get('config')
    async with async_session.begin() as session:
        active_movers = await session.execute(select(Mover).where(Mover.deleted == False))
        active_movers = active_movers.scalars().all()
        active_movers = [{'id': i.user.telegram_id, 'name': i.user.name} for i in active_movers]

    await call.message.edit_text('Активные перестановищики',
                                 reply_markup=inline_keyboards.get_mover_ref_list_keyboard(active_movers,
                                                                                           config.misc.items_per_page,
                                                                                           page, 'active'))


async def show_deleted_movers(call: CallbackQuery, callback_data: dict):
    page = int(callback_data['payload'])
    async_session: AsyncSession = call.bot.get('database')
    config = call.bot.get('config')
    async with async_session.begin() as session:
        active_movers = await session.execute(select(Mover).where(Mover.deleted == True))
        active_movers = active_movers.scalars().all()
        active_movers = [{'id': i.user.telegram_id, 'name': i.user.name} for i in active_movers]

    await call.message.edit_text('Удаленные перестановищики',
                                 reply_markup=inline_keyboards.get_mover_ref_list_keyboard(active_movers,
                                                                                           config.misc.items_per_page,
                                                                                           page, 'active'))


async def show_referral_info(call: CallbackQuery, callback_data: dict):
    telegram_id = int(callback_data['id'])
    action = callback_data['action']
    async_session: AsyncSession = call.bot.get('database')
    async with async_session.begin() as session:
        user = await session.get(User, telegram_id)
    if user.mover:
        is_active = not user.mover.deleted
    else:
        is_active = False

    await call.message.edit_text(messages.referral_info.format(
            telegram_id=user.telegram_id,
            name=user.name,
            level=user.referral.level,
            deals_count=user.referral.deals_count,
            ref_deals_count=user.referral.ref_deals_count,
            email=user.email,
            phone=user.phone
        ), reply_markup=inline_keyboards.get_referral_update_keyboard(user, is_active, action))
    await call.answer()


def register_movers_active_and_del(dp: Dispatcher):
    dp.register_callback_query_handler(show_active_movers, callbacks.movers.filter(to='active'))
    dp.register_callback_query_handler(show_deleted_movers, callbacks.movers.filter(to='deleted'))
    dp.register_callback_query_handler(show_referral_info, callbacks.movers_update.filter())
