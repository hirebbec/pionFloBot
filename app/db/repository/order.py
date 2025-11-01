from typing import Sequence

from db.models import Order
from db.repository.base import BaseDataBaseRepository
from sqlalchemy import insert, select


class OrderRepository(BaseDataBaseRepository):
    async def create(self, shift_id: int, amount: int) -> None:
        query = insert(Order).values(shift_id=shift_id, amount=amount)

        await self._session.execute(query)
        await self._session.commit()

    async def get_by_shift_id(self, shift_id: int) -> Sequence[Order]:
        query = select(Order).where(Order.shift_id == shift_id)

        result = await self._session.execute(query)
        return result.scalars().all()
