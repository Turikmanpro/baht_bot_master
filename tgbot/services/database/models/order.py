from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Boolean, Float, text, String, Integer
from sqlalchemy.orm import relationship

from tgbot.services.database.base import Base
from tgbot.services.database.models import User


class Order(Base):
    __tablename__ = 'bitrix_order'

    bitrix_id = Column(BigInteger, primary_key=True, autoincrement=True)

    exchange_type = Column(String(16), nullable=False)
    deal_type = Column(String(32), nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_telegram_id = Column(BigInteger, ForeignKey(User.telegram_id))
    phone_number = Column(String(16))
    customer_receive = Column(Float, nullable=False)
    customer_give = Column(Float, nullable=False)
    exchange_rate = Column(Float, nullable=False)

    courier_telegram_id = Column(BigInteger, ForeignKey('courier.telegram_id'))
    courier_earn = Column(Float, server_default='0.0')
    finished = Column(Boolean, server_default=text('false'))
    started_at = Column(DateTime, server_default=text('NOW()'))
    finished_at = Column(DateTime)
    stat_week_id = Column(BigInteger, ForeignKey('statistic.id'))

    sending_bank = Column(String(255), nullable=True)
    sending_bank_requisites = Column(String(255), nullable=True)
    receive_bank = Column(String(255), nullable=True)
    receive_bank_requisites = Column(String(255), nullable=True)

    network_type = Column(String(16), nullable=True)
    requisites = Column(String(255), nullable=True)

    location = Column(String(255), nullable=True)
    location_comment = Column(String(255), nullable=True)

    operator_id = Column(BigInteger, ForeignKey('operator.telegram_id'), nullable=True)
    answered_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    customer_answered_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    is_received = Column(Boolean, server_default=text('false'))

    is_canceled = Column(Boolean, server_default=text('false'))

    input_currency = Column(String(64), nullable=True)

    operator = relationship('Operator', back_populates='orders', uselist=False, lazy='selectin')
    customer = relationship('User', back_populates='orders', uselist=False, lazy='selectin')

    def set_attr(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
