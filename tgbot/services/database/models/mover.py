from sqlalchemy import Column, BigInteger, text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from tgbot.services.database.base import Base
from tgbot.services.database.models import User


class Mover(Base):
    __tablename__ = 'mover'

    telegram_id = Column(BigInteger, ForeignKey(User.telegram_id), primary_key=True)
    created_at = Column(DateTime(), server_default=text('NOW()'))
    deleted = Column(Boolean, server_default=text('false'))

    user = relationship('User', lazy='selectin', back_populates='mover', uselist=False)
    mover_orders = relationship('MoverOrder', lazy='selectin', back_populates='mover', uselist=True)
