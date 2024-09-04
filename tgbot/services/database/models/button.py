from sqlalchemy import Column, BigInteger, String

from tgbot.services.database.base import Base


class Button(Base):
    __tablename__ = 'button'

    id = Column(BigInteger, primary_key=True)
    button_name = Column(String(64))

    @classmethod
    async def insert_buttons(cls, db_session):
        async with db_session.begin() as session:
            exchange_rate = Button(id=1, button_name='exchange_rate')
            make_exchange = Button(id=2, button_name='make_exchange')

            if not await session.get(Button, 1): session.add(exchange_rate)
            if not await session.get(Button, 2): session.add(make_exchange)
