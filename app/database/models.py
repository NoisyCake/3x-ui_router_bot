from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, DateTime, Boolean, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass

class Client(Base):
    __tablename__ = 'clients'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True)
    contract_num: Mapped[int] = mapped_column(BigInteger, unique=True)
    subscription: Mapped[bool] = mapped_column(Boolean, default=False)
    exp_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    uuid: Mapped[str] = mapped_column(String, unique=True, nullable=True)