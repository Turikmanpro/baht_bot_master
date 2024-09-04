from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Integer, Float, text, String, Boolean

from tgbot.services.database.base import Base
from tgbot.services.database.models import Courier


class Statistic(Base):
    __tablename__ = 'statistic'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    courier_id = Column(BigInteger, ForeignKey(Courier.telegram_id))
    week_created_at = Column(DateTime(), server_default=text('NOW()'))
    courier_earned = Column(Float, server_default='0.0')
    operator_status = Column(Boolean, server_default='False')
    courier_status = Column(Boolean, server_default='False')
    completed_orders = Column(Integer, server_default='0')
    canceled_orders = Column(Integer, server_default='0')

