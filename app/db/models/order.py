from datetime import datetime

from sqlalchemy import Integer, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import BaseModel
from db.models.mixins import IDMixin


class Order(BaseModel, IDMixin):
    __tablename__ = "orders"

    shift_id: Mapped[int] = mapped_column(Integer, ForeignKey("shifts.id"))
    amount: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
