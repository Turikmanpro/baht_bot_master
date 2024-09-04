import datetime
from decimal import Decimal

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from isoweek import Week
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from tgbot.keyboards import inline_keyboards, reply_keyboards
from tgbot.misc import reply_commands, callbacks, messages, states
from tgbot.misc.helper import get_rate, get_orig_earned_factor
from tgbot.services import AsyncBinance
from tgbot.services.bitrix.bitrix_schemas import ExchangeType, DealType
from tgbot.services.database.models import Operator, Referral, User, Order, Statistic


async def send_operators(message: Message):
    await message.answer('Операторы', reply_markup=inline_keyboards.operators_menu)


async def send_settings(message: Message):
    config = message.bot.get('config')
    await message.answer(
        messages.settings.format(delivery_coef=config.misc.delivery_percent,
                                 transfer_coef=config.misc.transfer_percent),
        reply_markup=inline_keyboards.settings
    )


async def show_settings(call: CallbackQuery):
    config = call.bot.get('config')
    await call.message.edit_text(
        messages.settings.format(delivery_coef=config.misc.delivery_percent,
                                 transfer_coef=config.misc.transfer_percent),
        reply_markup=inline_keyboards.settings
    )
    await call.answer()


async def send_stats(message: Message):
    db_session = message.bot.get('database')
    async with db_session() as session:
        referrals = await session.execute(select(Referral))
        referrals = referrals.scalars().all()

    ref1_count = 0
    ref2_count = 0
    ref3_count = 0
    exchanges_sum = 0
    dividends_sum = 0
    for referral in referrals:
        if referral.level == 1:
            ref1_count += 1
        elif referral.level == 2:
            ref2_count += 1
        elif referral.level == 3:
            ref3_count += 1

        exchanges_sum += referral.red_deposit
        dividends_sum += referral.dividends_15

    await message.answer(
        messages.admin_stats.format(
            exchanges_sum=exchanges_sum,
            dividends_sum=dividends_sum,
            refs_count_1=ref1_count,
            refs_count_2=ref2_count,
            refs_count_3=ref3_count,
            refs_count=len(referrals)
        ),
        reply_markup=inline_keyboards.admin_stats
    )


async def show_ir_stats(call: CallbackQuery, callback_data: dict):
    ir_level = int(callback_data['payload'])
    db_session = call.bot.get('database')
    async with db_session() as session:
        records = await session.execute(select(Referral).where(Referral.original_referral_id == ir_level))
        referrals = records.scalars().all()

    rate_clicks = 0
    exchange_clicks = 0
    reg_count = 0
    orders_count = 0
    tr_transfer = 0
    tr_delivery = 0
    tu_transfer = 0
    tu_delivery = 0
    rt_transfer = 0
    rt_delivery = 0
    ut_transfer = 0
    ut_delivery = 0
    for referral in referrals:
        rate_clicks += len(list(filter(lambda click: click.button_id == 1, referral.user.clicks)))
        exchange_clicks += len(list(filter(lambda click: click.button_id == 2, referral.user.clicks)))
        reg_count += referral.user.is_reg
        orders_count += len(referral.user.orders)

        tr_orders = filter(lambda order: order.exchange_type == ExchangeType.THB_RUB, referral.user.orders)
        tr_transfer += len(list(filter(lambda order: order.deal_type in (DealType.RUS_TRANSFER, DealType.THAI_TRANSFER), tr_orders)))
        tr_delivery += len(list(filter(lambda order: order.deal_type in (DealType.CASH, DealType.COURIER), tr_orders)))

        tu_orders = filter(lambda order: order.exchange_type == ExchangeType.THB_USDT, referral.user.orders)
        tu_transfer += len(list(filter(lambda order: order.deal_type in (DealType.RUS_TRANSFER, DealType.THAI_TRANSFER), tu_orders)))
        tu_delivery += len(list(filter(lambda order: order.deal_type in (DealType.CASH, DealType.COURIER), tu_orders)))

        rt_orders = filter(lambda order: order.exchange_type == ExchangeType.RUB_THB, referral.user.orders)
        rt_transfer += len(list(filter(lambda order: order.deal_type in (DealType.RUS_TRANSFER, DealType.THAI_TRANSFER), rt_orders)))
        rt_delivery += len(list(filter(lambda order: order.deal_type in (DealType.CASH, DealType.COURIER), rt_orders)))

        ut_orders = filter(lambda order: order.exchange_type == ExchangeType.USDT_THB, referral.user.orders)
        ut_transfer += len(list(filter(lambda order: order.deal_type in (DealType.RUS_TRANSFER, DealType.THAI_TRANSFER), ut_orders)))
        ut_delivery += len(list(filter(lambda order: order.deal_type in (DealType.CASH, DealType.COURIER), ut_orders)))

    message_text = messages.ir_stats.format(
        ir_level=ir_level,
        start_clicks=len(referrals),
        rate_clicks=rate_clicks,
        exchange_clicks=exchange_clicks,
        reg_count=reg_count,
        orders_count=orders_count,
        tr_transfer=tr_transfer,
        tr_delivery=tr_delivery,
        tu_transfer=tu_transfer,
        tu_delivery=tu_delivery,
        rt_transfer=rt_transfer,
        rt_delivery=rt_delivery,
        ut_transfer=ut_transfer,
        ut_delivery=ut_delivery
    )

    await call.message.edit_text(message_text,
                                 reply_markup=inline_keyboards.get_back_keyboard('admin_stats'))
    await call.answer()


async def show_stats(call: CallbackQuery):
    db_session = call.bot.get('database')
    async with db_session() as session:
        referrals = await session.execute(
            select(Referral).where(Referral.id != 0, Referral.id != 1, Referral.id != 2, Referral.id != 3))
        referrals = (referrals.scalars().all())
        orders = await session.execute(select(Order).where(Order.finished))
        orders = orders.scalars().all()
        orig_referrals = await session.execute(select(Referral).where(Referral.is_original))
        orig_referrals = orig_referrals.scalars().all()
        # reg_0_count = await session.execute(select(func.count).select_from(User, Referral)
        #                                     .join(Referral.telegram_id)
        #                                     .where(User.is_reg == True, Referral.original_referral_id == 0))
        # reg_1_count = await session.execute(select(func.count).select_from(User, Referral)
        #                                     .join(Referral.telegram_id)
        #                                     .where(User.is_reg == True, Referral.original_referral_id == 1))
        # reg_2_count = await session.execute(select(func.count).select_from(User, Referral)
        #                                     .join(Referral.telegram_id)
        #                                     .where(User.is_reg == True, Referral.original_referral_id == 2))
        # reg_3_count = await session.execute(select(func.count).select_from(User, Referral)
        #                                     .join(Referral.telegram_id)
        #                                     .where(User.is_reg == True, Referral.original_referral_id == 3))

    ref1_count = 0
    reg1_count = 0
    ref2_count = 0
    reg2_count = 0
    ref3_count = 0
    reg3_count = 0
    ref0_count = 0
    reg0_count = 0

    for referral in referrals:
        if referral.original_referral_id == 1:
            ref1_count += 1
            if referral.user.is_reg: reg1_count += 1
        elif referral.original_referral_id == 2:
            ref2_count += 1
            if referral.user.is_reg: reg2_count += 1
        elif referral.original_referral_id == 3:
            ref3_count += 1
            if referral.user.is_reg: reg3_count += 1
        elif referral.original_referral_id == 0:
            ref0_count += 1
            if referral.user.is_reg: reg0_count += 1

    dividends_sum = 0
    dividends_0_sum = 0
    for orig_referral in orig_referrals:
        if orig_referral.id == 0:
            dividends_0_sum += orig_referral.red_deposit
        else:
            dividends_sum += orig_referral.red_deposit

    thb_ex_rate = await AsyncBinance.get_avg_price('THB', 'SELL')
    rub_ex_rate = await AsyncBinance.get_avg_price('RUB', 'SELL')

    exchanges_sum = Decimal(0.0)
    exchanges_0_sum = Decimal(0.0)
    for order in orders:
        ex_type = order.exchange_type
        input_currency, output_currency = ex_type.split('/')
        customer_give = Decimal(order.customer_give)
        # convert customer_give sum to usdt
        if input_currency == 'THB':
            if output_currency == 'USDT':
                plus = round(order.customer_receive, 3)
            else:  # RUB
                plus = round((customer_give / thb_ex_rate), 3)
        elif input_currency == 'RUB':
            plus = round((customer_give / rub_ex_rate), 3)
        else:
            plus = customer_give

        if order.customer.referral.original_referral_id == 0:
            exchanges_0_sum += Decimal(plus)
        else:
            exchanges_sum += Decimal(plus)

    await call.message.edit_text(
        messages.admin_stats.format(
            exchanges_sum=round(exchanges_sum),
            dividends_sum=round(dividends_sum),
            refs_count_0=ref0_count,
            refs_count_1=ref1_count,
            refs_count_2=ref2_count,
            refs_count_3=ref3_count,
            refs_count=len(referrals),
            dividends_0_sum=round(dividends_0_sum),
            exchanges_0_sum=round(exchanges_0_sum)
        ),
        reply_markup=inline_keyboards.admin_stats
    )
    await call.answer()


async def show_operators(call: CallbackQuery):
    await call.message.edit_text('Операторы', reply_markup=inline_keyboards.operators_menu)
    await call.answer()


async def send_referrals_level_choose(message: Message):
    db_session = message.bot.get('database')
    async with db_session() as session:
        records = await session.execute(select(Referral).where(Referral.is_original == True))
        referrals = records.scalars().all()

    await message.answer('Рефералы', reply_markup=inline_keyboards.get_referral_level_choose_keyboard(referrals, 'ref'))


async def start_delivery_percent_input(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Введите новое значение:', reply_markup=reply_keyboards.cancel)
    await states.SettingsState.waiting_for_percent.set()
    await state.update_data(type='delivery')
    await call.answer()


async def start_transfer_percent_input(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Введите новое значение:', reply_markup=reply_keyboards.cancel)
    await states.SettingsState.waiting_for_percent.set()
    await state.update_data(type='transfer')
    await call.answer()


async def get_new_percent(message: Message, state: FSMContext):
    new_percent = message.text
    try:
        new_percent = float(new_percent)
    except ValueError:
        await message.answer('Неверный формат. Попробуйте ещё раз:')
        return

    config = message.bot.get('config')
    async with state.proxy() as data:
        if data['type'] == 'delivery':
            config.misc.delivery_percent = new_percent
        else:
            config.misc.transfer_percent = new_percent

    db_session = message.bot.get('database')
    async with db_session.begin() as session:
        user = await session.get(User, message.from_id)

    keyboard = reply_keyboards.get_main_keyboard(show_reg_button=not user.is_reg, is_courier=user.courier)
    await message.answer('Успешно изменено!', reply_markup=keyboard)
    await state.finish()
    await send_settings(message)


async def show_active_operators(call: CallbackQuery):
    db_session = call.bot.get('database')
    async with db_session() as session:
        records = await session.execute(select(Operator).where(Operator.deleted == False))
        operators = records.scalars().all()

    await call.message.edit_text('Активные операторы',
                                 reply_markup=inline_keyboards.get_operators_keyboard(operators, True))
    await call.answer()


async def show_deleted_operators(call: CallbackQuery):
    db_session = call.bot.get('database')
    async with db_session() as session:
        records = await session.execute(select(Operator).where(Operator.deleted == True))
        operators = records.scalars().all()

    await call.message.edit_text('Удаленные операторы',
                                 reply_markup=inline_keyboards.get_operators_keyboard(operators, False))
    await call.answer()


async def show_operator(call: CallbackQuery, callback_data: dict):
    db_session = call.bot.get('database')
    async with db_session() as session:
        operator = await session.get(Operator, int(callback_data['id']))

    await call.message.edit_text(
        messages.operator_info.format(
            name=operator.user.name,
            id=operator.telegram_id,
            level=operator.user.referral.level,
            deals=operator.user.referral.deals_count,
            ref_deals=operator.user.referral.ref_deals_count,
            email=operator.user.email,
            phone=operator.user.phone
        ),
        reply_markup=inline_keyboards.get_operator_keyboard(operator.telegram_id, callback_data['action'])
    )
    await call.answer()


async def update_operator(call: CallbackQuery, callback_data: dict):
    db_session = call.bot.get('database')
    async with db_session.begin() as session:
        operator = await session.get(Operator, int(callback_data['id']))
        if operator:
            if callback_data['action'] == 'delete':
                operator.deleted = True
            elif callback_data['action'] == 'active':
                operator.deleted = False
        else:
            operator = Operator(telegram_id=int(callback_data['id']))
            session.add(operator)

    await call.answer('Успешно!', show_alert=True)
    await show_operators(call)


async def show_referral_level_choose(call: CallbackQuery, callback_data: dict):
    if callback_data['payload'] == 'add':
        text = 'Добавить оператора'
        action = 'oper'
        back_to = 'operators'
        back_payload = 'menu'
    else:
        text = 'Рефералы'
        action = 'ref'
        back_to = 'admin_menu'
        back_payload = ''

    db_session = call.bot.get('database')
    async with db_session() as session:
        records = await session.execute(select(Referral).where(Referral.is_original == True))
        referrals = records.scalars().all()

    keyboard = inline_keyboards.get_referral_level_choose_keyboard(referrals, action=action, back_to=back_to,
                                                                   back_payload=back_payload)
    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()


async def show_referral_type_choose(call: CallbackQuery, callback_data: dict):
    db_session = call.bot.get('database')
    async with db_session() as session:
        referral = await session.get(Referral, int(callback_data['level']))
    await call.message.edit_text(f'ИР {referral.user.name}',
                                 reply_markup=inline_keyboards.get_referral_type_choose_keyboard(
                                     callback_data['level']))
    await call.answer()


async def show_referrals(call: CallbackQuery, callback_data: dict):
    db_session = call.bot.get('database')
    async with db_session() as session:
        records = await session.execute(
            select(Referral).where(Referral.original_referral_id == int(callback_data['level']),
                                   Referral.is_original == False))
        referrals = records.scalars().all()
        orig_referral = await session.get(Referral, int(callback_data['level']))

    await call.message.edit_text(
        f'Рефералы {orig_referral.user.name}\nСписок рефералов с суммой обменов',
        reply_markup=inline_keyboards.get_referral_choose_keyboard(referrals)
    )
    await call.answer()


async def update_referral(call: CallbackQuery, callback_data: dict):
    db_session = call.bot.get('database')
    async with db_session.begin() as session:
        referral = await session.get(Referral, int(callback_data['id']))
        referral.is_blocked = not referral.is_blocked

    await call.answer('Успешно!', show_alert=True)
    await show_admin_menu(call)


async def show_referral(call: CallbackQuery, callback_data: dict):
    db_session = call.bot.get('database')
    async with db_session() as session:
        user = await session.get(User, int(callback_data['id']))

    if callback_data['action'] == 'oper':
        if user.operator:
            is_active = not user.operator.deleted
        else:
            is_active = False
        keyboard = inline_keyboards.get_referral_update_keyboard(user.referral.telegram_id, is_active,
                                                                 user.referral.original_referral_id)
    else:
        keyboard = inline_keyboards.get_referral_info_keyboard(not user.referral.is_blocked,
                                                               user.referral.original_referral_id, user.referral.id)

    await call.message.edit_text(
        messages.referral_info.format(
            telegram_id=user.referral.telegram_id,
            name=user.name,
            level=user.referral.level,
            deals_count=user.referral.deals_count,
            ref_deals_count=user.referral.ref_deals_count,
            email=user.email,
            phone=user.phone
        ),
        reply_markup=keyboard
    )
    await call.answer()


async def show_active_referrals(call: CallbackQuery, callback_data: dict):
    db_session = call.bot.get('database')
    async with db_session() as session:
        referrals = await session.execute(
            select(Referral).where(Referral.is_blocked == False).where(
                Referral.original_referral_id == int(callback_data['payload']), Referral.is_original == False)
        )
        referrals = referrals.scalars().all()
        orig_referral = await session.get(Referral, int(callback_data['payload']))

    await call.message.edit_text(f'Активные рефералы {orig_referral.user.name}',
                                 reply_markup=inline_keyboards.get_referral_choose_keyboard(referrals, action='ref',
                                                                                            level=callback_data[
                                                                                                'payload']))
    await call.answer()


async def show_blocked_referrals(call: CallbackQuery, callback_data: dict):
    db_session = call.bot.get('database')
    async with db_session() as session:
        referrals = await session.execute(
            select(Referral).where(Referral.is_blocked == True).where(
                Referral.original_referral_id == int(callback_data['payload']), Referral.is_original == False)
        )
        referrals = referrals.scalars().all()
        orig_referral = await session.get(Referral, int(callback_data['payload']))

    await call.message.edit_text(f'Заблокированные рефералы {orig_referral.user.name}',
                                 reply_markup=inline_keyboards.get_referral_choose_keyboard(referrals, action='ref',
                                                                                            level=callback_data[
                                                                                                'payload']))
    await call.answer()


async def show_admin_menu(call: CallbackQuery):
    await call.message.edit_text('Меню админа', reply_markup=inline_keyboards.admin_menu)
    await call.answer()


async def send_admin_menu(message: Message):
    config = message.bot.get('config')
    if message.from_id not in config.tg_bot.admin_ids:
        await message.answer('Вы не админ')
        return

    await message.answer('Меню админа', reply_markup=inline_keyboards.admin_menu)


async def show_admin_week_stat(call: CallbackQuery, callback_data: dict):
    year = callback_data['year']
    week = callback_data['value']  # number of week

    day = Week(int(year), int(week)).monday()
    async_session: AsyncSession = call.bot.get('database')
    async with async_session.begin() as session:
        stmn = f"SELECT * FROM bitrix_order WHERE started_at BETWEEN '{day}' AND '{day + datetime.timedelta(days=7)}'"
        week = (await session.execute(stmn)).all()
        records = await session.execute(select(Referral).where(Referral.is_original == True))
        orig_referrals = records.scalars().all()
    if week:
        await call.message.edit_text('Выбор исходного реферала',
                                     reply_markup=inline_keyboards.get_admin_stat(orig_referrals, day))
        await call.answer()
    else:
        await call.answer('Нет отчетных периодов', show_alert=True)


async def show_admin_stat_final(call: CallbackQuery, callback_data: dict):
    async_session: AsyncSession = call.bot.get('database')

    orig_id = int(callback_data['orig_id'])
    day = callback_data['start_day']  # day from week start
    day = datetime.datetime.strptime(day, '%Y-%m-%d')

    new_users = 0
    exchanges_sum = 0
    exchanges_count = 0
    dividends_sum = 0

    thb_ex_rate = float(await AsyncBinance.get_avg_price('THB', 'SELL'))
    rub_ex_rate = float(await AsyncBinance.get_avg_price('RUB', 'SELL'))

    async with async_session.begin() as session:
        max_ref_lvl = ((await session.execute(f'select max(level) from referral where original_referral_id = {orig_id}')).first())[0]
        print(max_ref_lvl)
        if not max_ref_lvl:
            await call.answer('Нет данных')
            return
        lvls_sum = [0] * max_ref_lvl
        lvls_count = [0] * max_ref_lvl
        print(lvls_count)
        stmn = f"SELECT * FROM statistic WHERE week_created_at BETWEEN '{day}' AND '{day + datetime.timedelta(days=7)}'"
        weeks = (await session.execute(stmn)).scalars().all()
        for week in weeks:
            week = await session.get(Statistic, week)
            orders = await session.execute(select(Order).where(Order.stat_week_id == week.id, Order.finished))
            orders = orders.scalars().all()
            for order in orders:
                if order.customer.referral.original_referral_id != orig_id:
                    continue
                ex_type = order.exchange_type
                input_currency, output_currency = ex_type.split('/')
                customer_give = order.customer_give
                # convert customer_give sum to usdt
                if input_currency == 'THB':
                    if output_currency == 'USDT':
                        plus = round(order.customer_receive, 3)
                    else:  # RUB
                        plus = round((customer_give / thb_ex_rate), 3)
                elif input_currency == 'RUB':
                    plus = round((customer_give / rub_ex_rate), 3)
                else:
                    plus = customer_give
                referral = order.customer.referral
                i = referral.level
                lvls_sum[i - 1] += await get_rate(order.customer_give, get_orig_earned_factor(i), order.exchange_type)
                if int(lvls_sum[i - 1]) == lvls_sum[i - 1]:
                    lvls_sum[i - 1] = int(lvls_sum[i - 1])
                lvls_count[i - 1] += 1
                if referral.original_referral_id == orig_id:
                    exchanges_sum += plus
                    exchanges_count += 1
            if week.courier_id in range(0, 4):
                if week.courier_id == orig_id:
                    dividends_sum += week.courier_earned
        dividents_msg = ''
        for i in range(max_ref_lvl):
            ref_count = len((await session.execute(
                select(Referral).where(Referral.level == i + 1, Referral.original_referral_id == orig_id))).all())
            dividents_msg += f'Дивиденды {i + 1} уровень - {round(lvls_sum[i])} USDT\n'
            dividents_msg += f'Кол-во обменов - {lvls_count[i]}\n'
            dividents_msg += f'Кол-во пользователей - {ref_count}\n\n'

    msg = messages.referral_stats.format(
        orig_ref=orig_id,
        # new_users=new_users,
        exchanges_sum=round(exchanges_sum),
        exchanges_count=exchanges_count,
        dividends_sum=round(dividends_sum)
    )
    msg += dividents_msg
    await call.message.edit_text(msg, reply_markup=inline_keyboards.get_back_keyboard('admin_stats'))

    await call.answer()


async def change_block(call: CallbackQuery, callback_data: dict):
    telegram_id = int(callback_data['payload'])
    async_session: AsyncSession = call.bot.get('database')
    async with async_session.begin() as session:
        referral = await session.execute(select(Referral).where(Referral.telegram_id == telegram_id))
        referral = (referral.scalars().all())[0]
        referral.is_blocked = not referral.is_blocked
    await call.message.edit_text('Меню админа', reply_markup=inline_keyboards.admin_menu)
    await call.answer()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(send_admin_menu, commands=['admin'])
    dp.register_message_handler(send_operators, text=reply_commands.admin_operators)
    dp.register_message_handler(send_referrals_level_choose, text=reply_commands.admin_refs)
    dp.register_message_handler(send_settings, text=reply_commands.admin_settings)
    dp.register_message_handler(send_stats, text=reply_commands.admin_stats)

    dp.register_callback_query_handler(show_admin_menu, callbacks.navigation.filter(to='admin_menu'))

    dp.register_callback_query_handler(start_delivery_percent_input, callbacks.navigation.filter(to='delivery_upd'))
    dp.register_callback_query_handler(start_transfer_percent_input, callbacks.navigation.filter(to='transfer_upd'))
    dp.register_message_handler(get_new_percent, state=states.SettingsState.waiting_for_percent)

    dp.register_callback_query_handler(show_referral_level_choose,
                                       callbacks.navigation.filter(to='operators', payload='add'))
    dp.register_callback_query_handler(show_referral_level_choose,
                                       callbacks.navigation.filter(to='referrals', payload='lvl'))
    dp.register_callback_query_handler(show_active_operators,
                                       callbacks.navigation.filter(to='operators', payload='active'))
    dp.register_callback_query_handler(show_deleted_operators,
                                       callbacks.navigation.filter(to='operators', payload='deleted'))
    dp.register_callback_query_handler(show_operators, callbacks.navigation.filter(to='operators', payload='menu'))
    dp.register_callback_query_handler(show_operator, callbacks.operator_choose.filter())
    dp.register_callback_query_handler(update_operator, callbacks.operator_update.filter())

    dp.register_callback_query_handler(show_referral_type_choose, callbacks.referral_level_choose.filter(action='ref'))
    dp.register_callback_query_handler(show_active_referrals, callbacks.navigation.filter(to='active_refs'))
    dp.register_callback_query_handler(show_blocked_referrals, callbacks.navigation.filter(to='block_refs'))

    dp.register_callback_query_handler(show_referrals, callbacks.referral_level_choose.filter(action='oper'))
    dp.register_callback_query_handler(show_referral, callbacks.referral_choose.filter())
    dp.register_callback_query_handler(update_referral, callbacks.referral_update.filter())

    dp.register_callback_query_handler(show_stats, callbacks.navigation.filter(to='admin_stats'))
    dp.register_callback_query_handler(show_ir_stats, callbacks.navigation.filter(to='ir_stats'))

    dp.register_callback_query_handler(show_settings, callbacks.navigation.filter(to='admin_settings'))
    dp.register_callback_query_handler(show_admin_week_stat, callbacks.week_choose.filter(action='ref'))
    dp.register_callback_query_handler(show_admin_stat_final, callbacks.admin_stat.filter())
