import asyncio
import logging
from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiosmtplib import SMTPRecipientsRefused, SMTPResponseException, SMTPConnectTimeoutError, SMTPServerDisconnected
from sqlalchemy.exc import IntegrityError

from tgbot.keyboards import reply_keyboards
from tgbot.misc import states, messages
from tgbot.services.database.models import User
from tgbot.services.utils import generate_confirm_code, is_email_valid


async def get_email(message: Message, state: FSMContext):
    email = message.text.lower()
    if not is_email_valid(email):
        await message.answer('Неверно указан почтовый адрес, попробуйте снова')
        return

    db_session = message.bot.get('database')
    try:
        async with db_session.begin() as session:
            user = await session.get(User, message.from_id)
            user.email = email
    except IntegrityError:
        await message.answer('Почта уже использована, попробуйте снова')
        return

    code = generate_confirm_code(4)
    mail = message.bot.get('mail')
    try:
        await mail.send_mail(
            to=email,
            subject=messages.mail_subject,
            text=messages.mail_text.format(code=code, username=message.from_id, time=datetime.now()),
        )
    except (SMTPRecipientsRefused, SMTPResponseException, SMTPConnectTimeoutError, asyncio.TimeoutError, SMTPServerDisconnected) as error:
        await message.answer('Произошла ошибка, попробуйте позже', reply_markup=ReplyKeyboardRemove())
        keyboard = reply_keyboards.get_main_keyboard(show_reg_button=not user.is_reg, is_courier=user.courier)
        await message.answer(messages.main_menu, reply_markup=keyboard)
        await state.finish()
        logging.error(f'({message.from_id}) error during sending email: {error}')
        return

    await message.answer(messages.confirm_code_request.format(email=email))
    await state.update_data(email=email, code=code)
    await states.RegistrationState.next()


async def get_confirm_code(message: Message, state: FSMContext):
    confirm_code = message.text
    async with state.proxy() as data:
        if confirm_code != data['code']:
            await message.answer(f'Неверный код подтверждения ({confirm_code}), попробуйте снова')
            return

    await message.answer(messages.phone_request, reply_markup=reply_keyboards.get_phone)
    await states.RegistrationState.next()


async def get_phone(message: Message, state: FSMContext):
    db_session = message.bot.get('database')
    async with db_session.begin() as session:
        user = await session.get(User, message.from_id)
        user.phone = message.contact.phone_number.replace('+', '')
        user.is_reg = True

    await message.answer(messages.successful_registration, reply_markup=ReplyKeyboardRemove())
    keyboard = reply_keyboards.get_main_keyboard(show_reg_button=not user.is_reg, is_courier=user.courier)
    await message.answer(messages.main_menu, reply_markup=keyboard)
    await state.finish()


def register_registration(dp: Dispatcher):
    dp.register_message_handler(get_email, state=states.RegistrationState.waiting_for_email)
    dp.register_message_handler(get_confirm_code, state=states.RegistrationState.waiting_for_email_confirm_code)
    dp.register_message_handler(get_phone, state=states.RegistrationState.waiting_for_phone, content_types=types.ContentTypes.CONTACT)
