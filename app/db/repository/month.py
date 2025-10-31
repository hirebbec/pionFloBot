from sqlalchemy import select, insert, and_, update, func
from db.models import Month
from db.repository.base import BaseDataBaseRepository


class MonthRepository(BaseDataBaseRepository):
    async def create(self, telegram_id: str) -> None:
        query = insert(Month).values(telegram_id=telegram_id)

        await self._session.execute(query)
        await self._session.commit()

    async def get_active_month(self, telegram_id: str) -> Month | None:
        query = select(Month).where(
            and_(Month.is_active.is_(True), Month.telegram_id == telegram_id)
        )
        result = await self._session.execute(query)

        return result.scalars().first()

    async def end_month(self, telegram_id: str) -> None:
        query = (
            update(Month)
            .values(is_active=False, end_time=func.now())
            .where(and_(Month.is_active.is_(True), Month.telegram_id == telegram_id))
        )

        await self._session.execute(query)
        await self._session.commit()
