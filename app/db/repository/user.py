from db.models import User
from db.repository.base import BaseDataBaseRepository
from sqlalchemy import insert, select


class UserRepository(BaseDataBaseRepository):
    async def create(self, telegram_id: int) -> None:
        query = insert(User).values(telegram_id=telegram_id)

        await self._session.execute(query)
        await self._session.commit()

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        query = select(User).where(User.telegram_id == telegram_id)

        result = await self._session.execute(query)
        return result.scalars().first()
