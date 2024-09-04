from sqlalchemy import Column, BigInteger, text, DateTime, String, select, insert, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from tgbot.services.database.base import Base


class User(Base):
    __tablename__ = 'telegram_user'

    telegram_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    name = Column(String(128))
    username = Column(String(128), nullable=True)
    email = Column(String(128), nullable=True, unique=True)
    phone = Column(String(20), nullable=True, unique=True)
    is_reg = Column(Boolean, server_default=text('false'))
    created_at = Column(DateTime(), server_default=text('NOW()'))
    referral_id = Column(BigInteger, ForeignKey(telegram_id))

    courier = relationship('Courier', lazy='selectin', back_populates='user', uselist=False)
    operator = relationship('Operator', lazy='selectin', back_populates='user', uselist=False)
    referral = relationship('Referral', lazy='selectin', foreign_keys='[Referral.telegram_id]', uselist=False)
    clicks = relationship('Click', lazy='selectin', uselist=True)
    orders = relationship('Order', lazy='selectin', uselist=True)
    mover = relationship('Mover', lazy='selectin', back_populates='user', uselist=False)

    @classmethod
    async def create_default_users(cls, db_session):
        async with db_session.begin() as session:
            user = await session.get(User, 0)
            if not user:
                user = User(
                    telegram_id=0,
                    name='Дефолтный',
                    referral_id=None
                )
                session.add(user)

            user = await session.get(User, 1)
            if not user:
                user = User(
                    telegram_id=1,
                    name='ИР1',
                    referral_id=None
                )
                session.add(user)

            user = await session.get(User, 2)
            if not user:
                user = User(
                    telegram_id=2,
                    name='ИР2',
                    referral_id=None
                )
                session.add(user)

            user = await session.get(User, 3)
            if not user:
                user = User(
                    telegram_id=3,
                    name='ИР3',
                    referral_id=None
                )
                session.add(user)
