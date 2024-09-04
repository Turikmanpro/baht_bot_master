from sqlalchemy import Column, BigInteger, Integer, text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship

from tgbot.services.database.base import Base
from tgbot.services.database.models import User


class Courier(Base):
    __tablename__ = 'courier'

    telegram_id = Column(BigInteger, ForeignKey(User.telegram_id), primary_key=True)
    earned = Column(Float, server_default='0.0')
    paid = Column(Float, server_default='0.0')
    canceled_orders_count = Column(Integer, server_default='0')
    created_at = Column(DateTime(), server_default=text('NOW()'))
    deleted = Column(Boolean, server_default=text('false'))
    is_free = Column(Boolean, server_default=text('true'))

    user = relationship('User', lazy='selectin', back_populates='courier', uselist=False)

    @classmethod
    async def create_default_couriers(cls, async_session):
        async with async_session.begin() as session:
            default_courier = await session.get(Courier, 0)
            if not default_courier:
                courier = Courier(
                    telegram_id=0
                )
                session.add(courier)
            default_courier = await session.get(Courier, 1)
            if not default_courier:
                courier = Courier(
                    telegram_id=1
                )
                session.add(courier)
            default_courier = await session.get(Courier, 2)
            if not default_courier:
                courier = Courier(
                    telegram_id=2
                )
                session.add(courier)
            default_courier = await session.get(Courier, 3)
            if not default_courier:
                courier = Courier(
                    telegram_id=3
                )
                session.add(courier)
