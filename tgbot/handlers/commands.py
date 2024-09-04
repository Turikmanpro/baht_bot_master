import logging
import datetime
from decimal import Decimal, ROUND_HALF_DOWN

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload
from sqlalchemy import select

from tgbot.handlers.exchange import get_ex_rate_with_percents
from tgbot.keyboards.inline_exchange_keyboards import exchange_start_menu
from tgbot.keyboards.inline_keyboards import get_reviews_link_keyboard
from tgbot.keyboards.inline_permutations_keyboards import choose_permutation
from tgbot.misc.helper import get_ref
from tgbot.misc import messages, reply_commands, states
from tgbot.keyboards import inline_keyboards, reply_keyboards
from tgbot.services import AsyncBinance
from tgbot.services.bitrix.bitrix_schemas import ExchangeType, DealType
from tgbot.services.database.models import User, Referral, Click


async def start(message: Message, state: FSMContext):
    await state.finish()
    config = message.bot.get('config')
    args = message.get_args()
    ref_id = None
    try:
        payload = decode_payload(args)

        if payload == 'ref1':
            ref_id = 1  # orig ref telegram_id
        elif payload == 'ref2':
            ref_id = 2
        elif payload == 'ref3':
            ref_id = 3
        elif payload:
            ref_id = int(payload)  # ref telegram_id
    except ValueError:
        logging.error(f'({message.from_user.id}) Invalid start link')

    await message.delete()

    db_session = message.bot.get('database')
    async with db_session.begin() as session:
        user = await session.get(User, message.from_id)
        if not user:
            user = User(telegram_id=message.from_id, referral_id=ref_id, name=message.from_user.full_name,
                        username=message.from_user.username)
            session.add(user)
            if ref_id:
                referral = await get_ref(session, ref_id)

                new_referral = Referral(telegram_id=message.from_id, senior_referral_id=referral.id,
                                        level=referral.level + 1, original_referral_id=referral.original_referral_id)
            else:
                new_referral = Referral(telegram_id=message.from_id, senior_referral_id=0, level=1,
                                        original_referral_id=0)
            session.add(new_referral)

    logging.info(f'User {message.from_user.mention} ({message.from_user.id}) started bot with referral {ref_id}')
    async with db_session.begin() as session:
        user = await session.get(User, message.from_id)
    keyboard = reply_keyboards.get_main_keyboard(show_reg_button=not user.is_reg, is_courier=user.courier)
    await message.answer_video(config.videos_id.start, caption=messages.main_menu, reply_markup=keyboard)


async def send_exchange_rate(message: Message, state: FSMContext):
    await state.finish()
    db_session = message.bot.get('database')
    async with db_session.begin() as session:
        new_click = Click(
            user_id=message.from_user.id,
            button_id=1
        )
        session.add(new_click)

    config = message.bot.get('config')

    usdt_avg_price = await AsyncBinance.get_avg_price('RUB', 'BUY', ['TinkoffNew'])
    thb_avg_price = await AsyncBinance.get_avg_price('THB', 'SELL')  # for usdt thb

    rub_thb_price = (usdt_avg_price / thb_avg_price).quantize(Decimal('1.000'), ROUND_HALF_DOWN)  # for rub thb

    del_coef = Decimal(1) + (Decimal(config.misc.delivery_percent) / Decimal(100))
    tran_coef = Decimal(1) + (Decimal(config.misc.transfer_percent) / Decimal(100))
    print(del_coef, tran_coef)
    print(rub_thb_price, thb_avg_price)
    tz = datetime.timezone(datetime.timedelta(hours=7), "Thai")

    await message.answer(
        messages.exchange_rate.format(
            time_and_date=datetime.datetime.now(tz=tz).strftime("%d.%m.%Y"),
            rt_delivery=get_ex_rate_with_percents(config, rub_thb_price, ExchangeType.RUB_THB, DealType.CASH),
            rt_transfer=get_ex_rate_with_percents(config, rub_thb_price, ExchangeType.RUB_THB, DealType.THAI_TRANSFER),
            ut_delivery=get_ex_rate_with_percents(config, thb_avg_price, ExchangeType.USDT_THB, DealType.COURIER),
            ut_transfer=get_ex_rate_with_percents(config, thb_avg_price, ExchangeType.USDT_THB, DealType.THAI_TRANSFER),
            tr_delivery=get_ex_rate_with_percents(config, rub_thb_price, ExchangeType.THB_RUB, DealType.CASH),
            tr_transfer=get_ex_rate_with_percents(config, rub_thb_price, ExchangeType.THB_RUB, DealType.RUS_TRANSFER),
            tu_delivery=get_ex_rate_with_percents(config, thb_avg_price, ExchangeType.THB_USDT, DealType.CASH),
            tu_transfer=get_ex_rate_with_percents(config, thb_avg_price, ExchangeType.THB_USDT, DealType.THAI_TRANSFER)
        ), reply_markup=inline_keyboards.order_calc
    )


async def send_about_us(message: Message, state: FSMContext):
    await state.finish()
    await message.answer(messages.about)


async def send_referral_menu(message: Message, state: FSMContext):
    await state.finish()
    config = message.bot.get('config')
    db_session = message.bot.get('database')
    async with db_session.begin() as session:
        referral = (await session.execute(select(Referral).where(Referral.telegram_id == message.from_id))).first()
        print(referral)
        if not referral:
            new_referral = Referral(telegram_id=message.from_id, senior_referral_id=1, level=1)
            session.add(new_referral)
    await message.answer_video(config.videos_id.earn_usdt, caption=messages.referral_menu, reply_markup=inline_keyboards.referral_menu)
    # await message.answer(messages.referral_menu, reply_markup=inline_keyboards.referral_menu)


async def send_reviews(message: Message, state: FSMContext):
    await state.finish()
    config = message.bot.get('config')
    await message.answer('Отзывы', reply_markup=get_reviews_link_keyboard(config.misc.reviews_channel_url))


async def send_exchange_menu(message: Message, state: FSMContext):
    await state.finish()
    db_session = message.bot.get('database')

    async with db_session.begin() as session:
        new_click = Click(
            user_id=message.from_user.id,
            button_id=2
        )
        session.add(new_click)

    async with db_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user.is_reg:
            await message.answer('В целях безопасности, пожалуйста зарегистрируйтесь для совершения обмена')
            return
        referral = await session.execute(select(Referral).where(Referral.telegram_id == message.from_user.id))
        referral = (referral.scalars().all())[0]
        if referral.is_blocked:
            await message.answer('Ваш аккаунт заблокирован. У вас нет доступа к обмену')
            return

    await message.answer(messages.exchange_menu, reply_markup=exchange_start_menu)


async def start_registration(message: Message, state: FSMContext):
    await state.finish()
    await message.answer(messages.email_request, reply_markup=reply_keyboards.cancel)

    await states.RegistrationState.waiting_for_email.set()


async def support_button(message: Message, state: FSMContext):
    await state.finish()
    await message.answer(f'Наша поддержка: {"@swapmarketsupport_bot"}')


async def permutations(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Безналичные и наличные операции в крупных объемах', reply_markup=choose_permutation)


async def rent(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Пока в разработке')


async def get_file_id(message: Message):
    file_id = message.video.file_id
    print(file_id)
    await message.answer(f'file_id видео: {file_id}')


def register_commands(dp: Dispatcher):
    dp.register_message_handler(send_exchange_menu, text=reply_commands.make_exchange, state='*')
    dp.register_message_handler(send_reviews, text=reply_commands.reviews, state='*')
    dp.register_message_handler(send_exchange_rate, text=reply_commands.exchange_rate, state='*')
    dp.register_message_handler(send_referral_menu, text=reply_commands.referral_menu, state='*')
    dp.register_message_handler(send_about_us, text=reply_commands.about, state='*')
    dp.register_message_handler(start_registration, text=reply_commands.registration, state='*')
    dp.register_message_handler(support_button, text=reply_commands.support, state='*')
    dp.register_message_handler(permutations, text=reply_commands.permutations, state='*')
    dp.register_message_handler(rent, text=reply_commands.rent, state='*')
    dp.register_message_handler(start, commands=['start'], state='*')
    dp.register_message_handler(get_file_id, content_types=['video'])
