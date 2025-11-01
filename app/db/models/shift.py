from datetime import datetime

from sqlalchemy import ForeignKey, Integer, Boolean, Float, DateTime, func, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import BaseModel
from db.models.mixins import IDMixin


class Shift(BaseModel, IDMixin):
    __tablename__ = "shifts"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id")
    )
    month_id: Mapped[int] = mapped_column(Integer, ForeignKey("months.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rate: Mapped[float] = mapped_column(Float)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
