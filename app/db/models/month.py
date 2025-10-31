import datetime

from sqlalchemy import Integer, ForeignKey, Boolean, Float, DateTime, func, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import BaseModel
from db.models.mixins import IDMixin


class Month(BaseModel, IDMixin):
    __tablename__ = "months"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    total: Mapped[float] = mapped_column(Float, default=0)
    count: Mapped[int] = mapped_column(Integer, default=0)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
