from db.models import Shift
from db.repository.base import BaseDataBaseRepository
from sqlalchemy import select, and_, insert


class ShiftRepository(BaseDataBaseRepository):
    async def create(self, telegram_id: int, month_id: int, rate: int):
        query = insert(Shift).values(
            telegram_id=telegram_id, month_id=month_id, rate=rate
        )

        await self._session.execute(query)
        await self._session.commit()

    async def get_active_shift(self, telegram_id: int) -> Shift | None:
        query = select(Shift).where(
            and_(Shift.is_active.is_(True), Shift.telegram_id == telegram_id)
        )
        result = await self._session.execute(query)

        return result.scalars().first()
