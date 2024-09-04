from sqlalchemy import Column, BigInteger, text, ForeignKey, Boolean, Integer, Float
from sqlalchemy.orm import relationship

from tgbot.services.database.base import Base
from tgbot.services.database.models import User


class Referral(Base):
    __tablename__ = 'referral'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, ForeignKey(User.telegram_id))
    is_original = Column(Boolean, server_default=text('false'))
    senior_referral_id = Column(BigInteger, ForeignKey('referral.id'))
    senior_referral_telegram_id = Column(BigInteger, ForeignKey(User.telegram_id))
    level = Column(Integer)
    deals_count = Column(Integer, server_default='0')
    ref_deals_count = Column(Integer, server_default='0')
    ref_balance = Column(Float, server_default='0')
    red_deposit = Column(Float, server_default='0')  # total sum for all time
    is_blocked = Column(Boolean, server_default=text('false'))
    dividends_15 = Column(Float, server_default='0')
    original_referral_id = Column(BigInteger, ForeignKey('referral.id'), nullable=True)
    lvl1_ref_balance = Column(Float,  server_default='0')
    lvl2_ref_balance = Column(Float, server_default='0')
    lvl3_ref_balance = Column(Float, server_default='0')

    user = relationship('User', lazy='selectin', back_populates='referral', foreign_keys=[telegram_id], uselist=False)

    @classmethod
    async def create_default_referrals(cls, db_session):
        async with db_session.begin() as session:
            default_ref = await session.get(Referral, 0)
            if not default_ref:
                ref = Referral(
                    id=0,
                    telegram_id=0,
                    level=0,
                    is_original=True,
                    original_referral_id=0
                )
                session.add(ref)

            default_ref = await session.get(Referral, 1)
            if not default_ref:
                ref = Referral(
                    id=1,
                    telegram_id=1,
                    level=0,
                    is_original=True,
                    original_referral_id=1
                )
                session.add(ref)

            default_ref = await session.get(Referral, 2)
            if not default_ref:
                ref = Referral(
                    id=2,
                    telegram_id=2,
                    level=0,
                    is_original=True,
                    original_referral_id=2
                )
                session.add(ref)

            default_ref = await session.get(Referral, 3)
            if not default_ref:
                ref = Referral(
                    id=3,
                    telegram_id=3,
                    level=0,
                    is_original=True,
                    original_referral_id=3
                )
                session.add(ref)
