from sqlalchemy import select, insert, and_
from db.models import Mouth
from db.repository.base import BaseDataBaseRepository


class MouthRepository(BaseDataBaseRepository):
    async def create(self, telegram_id: str) -> None:
        query = insert(Mouth).values(telegram_id=telegram_id)

        await self._session.execute(query)
        await self._session.commit()

    async def get_active_mouth(self, telegram_id: str):
        query = select(Mouth).where(
            and_(Mouth.is_active.is_(True), Mouth.telegram_id == telegram_id)
        )
        result = await self._session.execute(query)

        return result.scalars().first()
