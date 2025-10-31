from db.models import Order
from db.repository.base import BaseDataBaseRepository
from sqlalchemy import insert
from sqlalchemy.orm import Mapped


class OrderRepository(BaseDataBaseRepository):
    async def create(self, shift_id: Mapped[int], amount: int) -> None:
        query = insert(Order).values(shift_id=shift_id, amount=amount)

        await self._session.execute(query)
        await self._session.commit()
