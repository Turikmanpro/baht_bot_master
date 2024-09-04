from sqlalchemy import Column, BigInteger, ForeignKey, Float, String, DateTime, text
from sqlalchemy.orm import relationship

from tgbot.services.database.base import Base
from tgbot.services.database.models import User


class MoverOrder(Base):
    __tablename__ = 'mover_order'

    id = Column(BigInteger, primary_key=True)

    exchange_type = Column(String(16), nullable=False)
    deal_type = Column(String(32), nullable=False)
    customer_telegram_id = Column(BigInteger, ForeignKey(User.telegram_id))

    acceptance_city = Column(String(128), nullable=False)
    receive_place = Column(String(128), nullable=False)
    customer_give = Column(Float, nullable=False)
    customer_receive = Column(Float, nullable=True)
    exchange_rate = Column(Float, nullable=True)
    commission = Column(Float, nullable=True)

    created_at = Column(DateTime, server_default=text('NOW()'))
    answered_at = Column(DateTime, nullable=True)

    mover_id = Column(BigInteger, ForeignKey('mover.telegram_id'), nullable=True)

    mover = relationship('Mover', back_populates='mover_orders', uselist=False, lazy='selectin')
