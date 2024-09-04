from decimal import Decimal, ROUND_HALF_DOWN

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ContentTypes
from aiogram_broadcaster import TextBroadcaster
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.keyboards import reply_keyboards
from tgbot.keyboards.inline import get_operator_order_keyboard
from tgbot.keyboards.inline_exchange_keyboards import *
from tgbot.keyboards.inline_keyboards import get_bank_choose_keyboard
from tgbot.keyboards.reply_keyboards import cancel, get_location, bank_choose, exchange_cancel_with_sum, \
    exchange_cancel_with_sum_thb
from tgbot.misc import states, callbacks, messages
from tgbot.misc.messages import get_courier_delivery_message
from tgbot.services import AsyncBinance
from tgbot.services.bitrix.bitrix_schemas import ExchangeType, DealType
from tgbot.services.database.models import User, Order


async def show_non_cash_exchange_menu(call: CallbackQuery):
    await call.message.edit_text('Безнал', reply_markup=non_cash_exchange_menu)
    await call.answer()


async def show_cash_exchange_menu(call: CallbackQuery):
    await call.message.edit_text('Наличные', reply_markup=cash_exchange_menu)


async def show_input_currency_menu(call: CallbackQuery, callback_data: dict, state: FSMContext):
    ex_type = callback_data['ex_type']
    deal_type = callback_data['deal_type']

    await call.message.delete()
    await call.message.answer(deal_type, reply_markup=get_input_currency_menu(ex_type, deal_type))
    await state.update_data(ex_type=ex_type, deal_type=deal_type)
    await call.answer()


async def ex_amount_input(call: CallbackQuery, callback_data: dict, state: FSMContext):
    input_currency = callback_data['payload']

    if input_currency == 'THB':
        keyboard = exchange_cancel_with_sum_thb
    else:
        keyboard = exchange_cancel_with_sum
    await call.message.answer(f'Введите сумму в {input_currency}', reply_markup=keyboard)

    await state.update_data(input_currency=input_currency)
    await states.ExchangeAmountState.waiting_for_sum.set()
    await call.answer()


async def get_exchange_rate(ex_type: ExchangeType):
    # client want to display only thb_rub and usdt_thb rates
    if ex_type in (ExchangeType.RUB_THB, ExchangeType.THB_RUB):
        thb_rub_rate = await AsyncBinance.get_rub_thb_exchange_rate()  # thb_rub
        return thb_rub_rate
    elif ex_type in (ExchangeType.USDT_THB, ExchangeType.THB_USDT):
        thb_avg_price = await AsyncBinance.get_avg_price('THB', 'SELL')  # usdt_thb
        return thb_avg_price
    # elif ex_type == ExchangeType.THB_RUB:
    #     thb_rub_rate = await AsyncBinance.get_rub_thb_exchange_rate()  # thb_rub
    #     print(ex_type, (1 / thb_rub_rate).quantize(Decimal('1.000')))
    #     return (1 / thb_rub_rate).quantize(Decimal('1.000'))
    # elif ex_type == ExchangeType.THB_USDT:
    #     thb_avg_price = await AsyncBinance.get_avg_price('THB', 'SELL')  # usdt_thb
    #     print(ex_type, (1 / thb_avg_price).quantize(Decimal('1.000')))
    #     return (1 / thb_avg_price).quantize(Decimal('1.000'))


def get_amounts(ex_type: ExchangeType, input_currency: str, input_amount: Decimal, ex_rate: Decimal):
    currency1, currency2 = ex_type.split('/')
    if ex_type == ExchangeType.RUB_THB:
        if input_currency == currency1:
            customer_give = input_amount
            customer_receive = (input_amount / ex_rate).quantize(Decimal('1.000'))
        else:
            customer_give = input_amount * ex_rate
            customer_receive = input_amount
    elif ex_type == ExchangeType.THB_RUB:
        if input_currency == currency1:
            customer_give = input_amount
            customer_receive = input_amount * ex_rate
        else:
            customer_give = (input_amount / ex_rate).quantize(Decimal('1.000'))
            customer_receive = input_amount
    elif ex_type == ExchangeType.THB_USDT:
        if input_currency == currency1:
            customer_give = input_amount
            customer_receive = (input_amount / ex_rate).quantize(Decimal('1.000'))
        else:
            customer_give = input_amount * ex_rate
            customer_receive = input_amount
    elif ex_type == ExchangeType.USDT_THB:
        if input_currency == currency1:
            customer_give = input_amount
            customer_receive = input_amount * ex_rate
        else:
            customer_give = (input_amount / ex_rate).quantize(Decimal('1.000'))
            customer_receive = input_amount

    return customer_give.quantize(Decimal('1')), customer_receive.quantize(Decimal('1'))


def get_ex_rate_with_percents(config, ex_rate, ex_type, deal_type) -> Decimal:
    tran_per = (config.misc.transfer_percent / 100)
    del_per = (config.misc.delivery_percent / 100)
    if deal_type == DealType.RUS_TRANSFER or deal_type == DealType.THAI_TRANSFER:
        if ex_type in (ExchangeType.THB_USDT, ExchangeType.RUB_THB, ExchangeType.USDT_RUB):
            ex_rate *= Decimal(1 + tran_per).quantize(Decimal('1.000'))
        else:
            ex_rate *= Decimal(1 - tran_per).quantize(Decimal('1.000'))
    else:  # cash and courier
        if ex_type in (ExchangeType.THB_USDT, ExchangeType.RUB_THB, ExchangeType.USDT_RUB):
            ex_rate *= Decimal(1 + del_per).quantize(Decimal('1.000'))
        else:
            ex_rate *= Decimal(1 - del_per).quantize(Decimal('1.000'))
    return ex_rate.quantize(Decimal('1.000'), ROUND_HALF_DOWN)


async def get_ex_amount(message: Message, state: FSMContext):
    config = message.bot.get('config')

    try:
        input_amount = Decimal(message.text)
    except ValueError:
        await message.answer('Неверная сумма. Укажите число.')
        return

    async with state.proxy() as data:
        ex_type = data['ex_type']
        deal_type = data['deal_type']
        input_currency = data['input_currency']

    # check input amount
    if deal_type in (DealType.RUS_TRANSFER, DealType.THAI_TRANSFER):
        cap = 5000
        sum_err_mes = 'При обмене на счет, минимальная сумма к обмену 5000 THB'
    else:
        cap = 45000
        sum_err_mes = 'При обмене с доставкой, минимальная сумма к обмену 45000 THB'

    ex_rate = await get_exchange_rate(ex_type)
    ex_rate = get_ex_rate_with_percents(config, ex_rate, ex_type, deal_type)

    currency1, currency2 = ex_type.split('/')
    customer_give, customer_receive = get_amounts(ex_type, input_currency, input_amount, ex_rate)
    print(ex_type, customer_give, customer_receive, ex_rate)
    if currency2 == 'THB':
        customer_receive = round(customer_receive / 100) * 100

    if input_currency == 'THB':
        if input_amount < cap:
            await message.answer(sum_err_mes)
            return
    else:
        if customer_receive < cap:
            await message.answer(sum_err_mes)
            return

    await state.update_data(
        ex_rate=float(ex_rate),
        customer_give=customer_give,
        customer_receive=customer_receive
    )
    await states.ExchangeAmountState.waiting_for_data.set()
    await message.answer('Ваша заявка', reply_markup=cancel)

    await message.answer(
        messages.pre_order_message.format(customer_give, currency1, customer_receive, currency2, ex_rate),
        reply_markup=ex_amount_keyboard)


async def make_deal(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        ex_type = data['ex_type']
        deal_type = data['deal_type']
        input_currency = data['input_currency']

    if deal_type == DealType.THAI_TRANSFER:
        if ex_type == ExchangeType.RUB_THB:

            await call.message.edit_text('Выберите ваш банк, с которого будете делать перевод',
                                         reply_markup=get_bank_choose_keyboard('rub_bank', 'inp_amount',
                                                                               'second_stage', input_currency))
        elif ex_type == ExchangeType.USDT_THB:
            await call.message.edit_text('Выберите вашу сеть',
                                         reply_markup=get_usdt_network_choose_keyboard('usdt', 'inp_amount',
                                                                                       'second_stage', input_currency))
        elif ex_type == ExchangeType.THB_USDT:
            await call.message.edit_text('Выберите Тайский банк, с которого будете делать перевод',
                                         reply_markup=get_thai_bank_choose_keyboard('thai_bank', 'inp_amount',
                                                                                    'second_stage', input_currency))
        await states.ExchangeAmountState.waiting_for_crm.set()
    elif deal_type == DealType.RUS_TRANSFER:
        if ex_type == ExchangeType.THB_RUB:
            await call.message.edit_text('Выберите Тайский банк',
                                         reply_markup=get_thai_bank_choose_keyboard('thai_bank', 'inp_amount',
                                                                                    'second_stage', input_currency))
        await states.ExchangeAmountState.waiting_for_crm.set()
    elif deal_type == DealType.COURIER or deal_type == DealType.CASH:
        await call.message.delete()
        await call.message.answer(
            'Куда отправить курьера? (передайте геопозицию или отправьте ссылку на место в Google Картах)',
            reply_markup=get_location)
        await states.ExchangeAmountState.waiting_for_location.set()

    await call.answer()


async def show_location_menu(message: Message, state: FSMContext):
    location = dict(message.location)
    location_link = f'https://maps.google.com/maps?q={location["latitude"]},{location["longitude"]}'
    print(location_link)
    await state.update_data(location=location_link)
    await states.ExchangeAmountState.waiting_for_location_comment.set()
    await message.answer('Введите название вашего местоположения (отель, вилла, кафе)', reply_markup=cancel)


async def get_manual_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await states.ExchangeAmountState.waiting_for_location_comment.set()
    await message.answer('Введите название вашего местоположения (отель, вилла, кафе)', reply_markup=cancel)


async def get_location_comment(message: Message, state: FSMContext):
    async with state.proxy() as data:
        ex_type = data['ex_type']
        deal_type = data['deal_type']
        input_currency = data['input_currency']

    location_comment = message.text
    await state.update_data(location_comment=location_comment)
    await states.ExchangeAmountState.waiting_for_crm.set()

    if deal_type == DealType.COURIER:
        if ex_type == ExchangeType.USDT_THB:
            await message.answer('Выберите вашу сеть',
                                 reply_markup=get_usdt_network_choose_keyboard('usdt', 'inp_amount',
                                                                               'fourth_stage', input_currency))
    elif deal_type == DealType.CASH:
        if ex_type == ExchangeType.THB_RUB:
            await message.answer('Выберите ваш банк, на который вы получаете RUB',
                                 reply_markup=get_bank_choose_keyboard('rub_bank', 'inp_amount', 'third_stage', input_currency))
        elif ex_type == ExchangeType.RUB_THB:
            await message.answer('Выберите ваш банк, с которого будете отправлять RUB',
                                 reply_markup=bank_choose)
            await states.ExchangeAmountState.waiting_for_requisites.set()
        elif ex_type == ExchangeType.THB_USDT:
            await message.answer('Выберите вашу сеть',
                                 reply_markup=get_usdt_network_choose_keyboard('usdt', 'inp_amount',
                                                                               'third_stage', input_currency))


async def make_deal_second_stage(call: CallbackQuery, callback_data: dict, state: FSMContext):
    print('second_stage')
    async with state.proxy() as data:
        ex_type = data['ex_type']
        deal_type = data['deal_type']
        input_currency = data['input_currency']

    bank = callback_data['bank']

    if deal_type == DealType.THAI_TRANSFER:
        if ex_type == ExchangeType.RUB_THB or ex_type == ExchangeType.USDT_THB:
            await state.update_data(sending_bank=bank)
            await call.message.edit_text('Выберите ваш Тайский банк, на который хотите получить THB',
                                         reply_markup=get_thai_bank_choose_keyboard('thai_bank', 'inp_amount',
                                                                                    'third_stage', input_currency))
        elif ex_type == ExchangeType.THB_USDT:
            await state.update_data(sending_bank=bank)
            await call.message.edit_text('Выберите вашу сеть',
                                         reply_markup=get_usdt_network_choose_keyboard('usdt', 'inp_amount',
                                                                                       'third_stage', input_currency))
    elif deal_type == DealType.RUS_TRANSFER:
        if ex_type == ExchangeType.THB_RUB:
            await state.update_data(sending_bank=bank)
            await call.message.edit_text('Выберите ваш банк, на который вы получаете RUB',
                                         reply_markup=get_bank_choose_keyboard('rub_bank', 'inp_amount', 'third_stage', input_currency))

    await call.answer()


async def make_deal_third_stage(call: CallbackQuery, callback_data: dict, state: FSMContext):
    print('third_stage')
    async with state.proxy() as data:
        ex_type = data['ex_type']
        deal_type = data['deal_type']
    await states.ExchangeAmountState.waiting_for_requisites.set()
    await call.message.delete()

    if deal_type == DealType.THAI_TRANSFER:
        await state.update_data(receive_bank=callback_data['bank'])
        if ex_type == ExchangeType.RUB_THB or ex_type == ExchangeType.USDT_THB:
            await call.message.answer('Введите номер банковского аккаунта тайского банка', reply_markup=cancel)
        elif ex_type == ExchangeType.THB_USDT:
            await call.message.answer('Введите реквизиты кошелька или BINANCE PAY ID для получения USDT',
                                      reply_markup=cancel)
    elif deal_type == DealType.RUS_TRANSFER:
        if ex_type == ExchangeType.THB_RUB:
            await state.update_data(receive_bank=callback_data['bank'])
            await call.message.answer('Введите номер карты русского банка',
                                      reply_markup=cancel)
    # elif deal_type == DealType.COURIER:
    #     if ex_type == ExchangeType.USDT_THB:
    #         await state.update_data(receive_bank=callback_data['bank'])
    #         await call.message.answer('вот это все таки надо скипать',
    #                                   reply_markup=cancel)
    elif deal_type == DealType.CASH:
        if ex_type == ExchangeType.THB_RUB:
            await state.update_data(receive_bank=callback_data['bank'])
            await call.message.answer('Введите номер карты русского банка',
                                      reply_markup=cancel)
        elif ex_type == ExchangeType.THB_USDT:
            await state.update_data(sending_bank=callback_data['bank'])
            await call.message.answer('Введите реквизиты кошелька или BINANCE PAY ID для получения USDT',
                                      reply_markup=cancel)
    await call.answer()


def get_custom_fields(order: Order):
    ex_type = order.exchange_type
    deal_type = order.deal_type
    if deal_type == DealType.THAI_TRANSFER:
        if ex_type == ExchangeType.RUB_THB or ex_type == ExchangeType.THB_USDT:
            custom_data = {'sending_bank': order.sending_bank, 'receive_bank': order.receive_bank,
                           'receive_bank_requisites': order.receive_bank_requisites}
        elif ex_type == ExchangeType.USDT_THB:
            custom_data = {'network_type': order.network_type, 'receive_bank': order.receive_bank,
                           'receive_bank_requisites': order.receive_bank_requisites}
    elif deal_type == DealType.RUS_TRANSFER:
        if ex_type == ExchangeType.THB_RUB:
            custom_data = {'receive_bank': order.receive_bank,
                           'receive_bank_requisites': order.receive_bank_requisites}
    elif deal_type == DealType.COURIER:
        if ex_type == ExchangeType.USDT_THB:
            custom_data = {'network_type': order.network_type,
                           'location': order.location,
                           'location_comment': order.location_comment}
    elif deal_type == DealType.CASH:
        if ex_type == ExchangeType.THB_RUB:
            custom_data = {'receive_bank': order.receive_bank,
                           'receive_bank_requisites': order.receive_bank_requisites, 'location': order.location,
                           'location_comment': order.location_comment}
        elif ex_type == ExchangeType.RUB_THB:
            custom_data = {'sending_bank': order.sending_bank, 'location': order.location,
                           'location_comment': order.location_comment}
        elif ex_type == ExchangeType.THB_USDT:
            custom_data = {'network_type': order.network_type, 'sending_bank_requisites': order.sending_bank_requisites,
                           'location': order.location, 'location_comment': order.location_comment}

    return custom_data


async def make_deal_courier_fourth_stage(call: CallbackQuery, callback_data: dict, state: FSMContext):
    async_session: AsyncSession = call.bot.get('database')

    async with state.proxy() as data:
        ex_type = data['ex_type']
        deal_type = data['deal_type']

        ex_rate = data['ex_rate']
        customer_give = data['customer_give']
        customer_receive = data['customer_receive']
        input_currency = data['input_currency']
    await state.finish()
    currency1, currency2 = ex_type.split('/')
    if currency2 == 'THB':
        customer_receive = round(customer_receive / 100) * 100
    message_data = [currency1, customer_give, currency2, customer_receive, ex_rate]

    # get main menu
    async with async_session.begin() as session:
        user = await session.get(User, call.from_user.id)
        keyboard = reply_keyboards.get_main_keyboard(show_reg_button=not user.is_reg, is_courier=user.courier)
    main_order_data = [ex_type, deal_type, user.name, user.telegram_id, user.phone, customer_receive, customer_give,
                       ex_rate]

    if deal_type == DealType.COURIER:
        location_comment = str(data['location_comment'])
        if ex_type == ExchangeType.USDT_THB:
            location = str(data['location'])
            receive_bank = callback_data['bank']
            custom_data = {'network_type': receive_bank,
                           'location': location,
                           'location_comment': location_comment}

    # append to db
    async with async_session.begin() as session:
        new_order = Order(
            exchange_type=ex_type,
            deal_type=deal_type,
            customer_name=user.name,
            customer_telegram_id=user.telegram_id,
            phone_number=user.phone,
            customer_receive=customer_receive,
            customer_give=customer_give,
            exchange_rate=ex_rate,
            input_currency=input_currency
        )

        session.add(new_order)
        order_id = new_order.bitrix_id

        new_order.set_attr(**custom_data)
        statement = f'select telegram_id from operator where deleted=false'
        operators_id = (await session.execute(statement)).scalars().all()

    message_data.append(user.phone)
    message_data.append(user.name)
    await call.message.answer(messages.get_formed_deal_message(ex_type, deal_type, message_data, custom_data),
                              reply_markup=keyboard)
    async with async_session.begin() as session:
        new_order = (await session.execute(select(Order).where(
            Order.customer_telegram_id == user.telegram_id,
            Order.customer_receive == customer_receive,
            Order.customer_give == customer_give,
            Order.exchange_rate == ex_rate
        ))).scalars().one()
        order_id = new_order.bitrix_id
        username = new_order.customer.username
        print(order_id, username)

    # send notify to operator
    message_text = get_courier_delivery_message(new_order, new_order.customer.username)
    await TextBroadcaster(
        chats=operators_id,
        text='Новый заказ.\n\n' + message_text,
        reply_markup=get_operator_order_keyboard(order_id)
    ).run()


async def make_deal_fourth_stage(message: Message, state: FSMContext):
    async_session: AsyncSession = message.bot.get('database')

    async with state.proxy() as data:
        ex_type = data['ex_type']
        deal_type = data['deal_type']

        ex_rate = data['ex_rate']
        customer_give = data['customer_give']
        customer_receive = data['customer_receive']
        input_currency = data['input_currency']

    print(customer_give, customer_receive, ' 4 stage begining')
    await state.finish()
    currency1, currency2 = ex_type.split('/')
    if currency2 == 'THB':
        customer_receive = round(customer_receive / 100) * 100
    message_data = [currency1, customer_give, currency2, customer_receive, ex_rate]

    # get main menu
    async with async_session.begin() as session:
        user = await session.get(User, message.from_id)
        keyboard = reply_keyboards.get_main_keyboard(show_reg_button=not user.is_reg, is_courier=user.courier)

    if deal_type == DealType.THAI_TRANSFER:
        sending_bank = data['sending_bank']
        receive_bank = data['receive_bank']
        receive_bank_requisites = message.text
        if ex_type == ExchangeType.RUB_THB:
            custom_data = {'sending_bank': sending_bank, 'receive_bank': receive_bank,
                           'receive_bank_requisites': receive_bank_requisites}
        elif ex_type == ExchangeType.USDT_THB:
            custom_data = {'network_type': sending_bank, 'receive_bank': receive_bank,
                           'receive_bank_requisites': receive_bank_requisites}
        elif ex_type == ExchangeType.THB_USDT:
            custom_data = {'sending_bank': sending_bank, 'receive_bank': receive_bank,
                           'receive_bank_requisites': receive_bank_requisites}
    elif deal_type == DealType.RUS_TRANSFER:
        sending_bank = data['sending_bank']
        receive_bank = data['receive_bank']
        receive_bank_requisites = message.text
        if ex_type == ExchangeType.THB_RUB:
            custom_data = {'receive_bank': receive_bank,
                           'receive_bank_requisites': receive_bank_requisites}
    elif deal_type == DealType.COURIER:
        location_comment = str(data['location_comment'])
        if ex_type == ExchangeType.USDT_THB:
            location = str(data['location'])

            receive_bank = data['receive_bank']

            custom_data = {'network_type': receive_bank,
                           'location': location,
                           'location_comment': location_comment}
    elif deal_type == DealType.CASH:
        location_comment = str(data['location_comment'])
        location = str(data['location'])
        if ex_type == ExchangeType.THB_RUB:
            custom_data = {'receive_bank': data['receive_bank'],
                           'receive_bank_requisites': message.text, 'location': location,
                           'location_comment': location_comment}
        elif ex_type == ExchangeType.RUB_THB:
            custom_data = {'sending_bank': message.text, 'location': location, 'location_comment': location_comment}
        elif ex_type == ExchangeType.THB_USDT:
            sending_bank = data['sending_bank']
            sending_bank_requisites = message.text
            custom_data = {'network_type': sending_bank, 'sending_bank_requisites': sending_bank_requisites,
                           'location': location, 'location_comment': location_comment}

    # append to db
    async with async_session.begin() as session:
        new_order = Order(
            exchange_type=ex_type,
            deal_type=deal_type,
            customer_name=user.name,
            customer_telegram_id=user.telegram_id,
            phone_number=user.phone,
            customer_receive=customer_receive,
            customer_give=customer_give,
            exchange_rate=ex_rate,
            input_currency=input_currency
        )

        new_order.set_attr(**custom_data)
        session.add(new_order)
    async with async_session.begin() as session:
        new_order = (await session.execute(select(Order).where(
            Order.customer_telegram_id == user.telegram_id,
            Order.customer_receive == customer_receive,
            Order.customer_give == customer_give,
            Order.exchange_rate == ex_rate
        ))).scalars().one()
        order_id = new_order.bitrix_id
        username = new_order.customer.username
        print(order_id, username)
        statement = f'select telegram_id from operator where deleted=false'
        operators_id = (await session.execute(statement)).scalars().all()
    print(customer_give, customer_receive, ' 4 stage end')
    message_data.append(user.phone)
    message_data.append(user.name)
    await message.answer(messages.get_formed_deal_message(ex_type, deal_type, message_data, custom_data),
                         reply_markup=keyboard)

    # send notify to operator
    message_text = get_courier_delivery_message(new_order, username)
    await TextBroadcaster(
        chats=operators_id,
        text='Новый заказ.\n\n' + message_text,
        reply_markup=get_operator_order_keyboard(order_id)
    ).run()


def register_exchange(dp: Dispatcher):
    # dp.register_callback_query_handler(show_non_cash_exchange_menu, callbacks.navigation.filter(to='non_cash_ex'))
    dp.register_callback_query_handler(show_input_currency_menu, callbacks.exchange.filter())
    dp.register_callback_query_handler(ex_amount_input, callbacks.navigation.filter(to='inp_amount'), state='*')
    dp.register_message_handler(get_ex_amount, state=states.ExchangeAmountState.waiting_for_sum)
    dp.register_callback_query_handler(make_deal, callbacks.navigation.filter(to='make_deal'),
                                       state=states.ExchangeAmountState.waiting_for_data)
    dp.register_callback_query_handler(make_deal_second_stage, callbacks.bank_choose.filter(payload='second_stage'),
                                       state=states.ExchangeAmountState.waiting_for_crm)
    dp.register_callback_query_handler(make_deal_third_stage, callbacks.bank_choose.filter(payload='third_stage'),
                                       state=states.ExchangeAmountState.waiting_for_crm)
    dp.register_callback_query_handler(make_deal_courier_fourth_stage,
                                       callbacks.bank_choose.filter(payload='fourth_stage'),
                                       state=states.ExchangeAmountState.waiting_for_crm)
    dp.register_message_handler(make_deal_fourth_stage, state=states.ExchangeAmountState.waiting_for_requisites)
    dp.register_message_handler(show_location_menu, state=states.ExchangeAmountState.waiting_for_location,
                                content_types=ContentTypes.LOCATION)
    dp.register_message_handler(get_manual_location, state=states.ExchangeAmountState.waiting_for_location)
    # dp.register_callback_query_handler(show_cash_exchange_menu, callbacks.navigation.filter(to='cash_ex'))
    dp.register_message_handler(get_location_comment, state=states.ExchangeAmountState.waiting_for_location_comment)
