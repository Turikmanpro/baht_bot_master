from sqlalchemy import Column, BigInteger, text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from tgbot.services.database.base import Base
from tgbot.services.database.models import User


class Operator(Base):
    __tablename__ = 'operator'

    telegram_id = Column(BigInteger, ForeignKey(User.telegram_id), primary_key=True)
    is_support = Column(Boolean, server_default=text('false'))
    created_at = Column(DateTime(), server_default=text('NOW()'))
    deleted = Column(Boolean, server_default=text('false'))

    user = relationship('User', lazy='selectin', back_populates='operator', uselist=False)
    orders = relationship('Order', lazy='selectin', back_populates='operator', uselist=True)
