from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Integer, Float, text, String, Boolean
from sqlalchemy.orm import relationship

from tgbot.services.database.base import Base
from tgbot.services.database.models import User
from tgbot.services.database.models.button import Button


class Click(Base):
    __tablename__ = 'click'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.telegram_id))
    button_id = Column(BigInteger, ForeignKey(Button.id))

    user = relationship('User', lazy='selectin', back_populates='clicks', uselist=False)
