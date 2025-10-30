from sqlalchemy import select

from db.models import Mouth
from db.repository.base import BaseDataBaseRepository


class MouthRepository(BaseDataBaseRepository):
    async def get_active_mouth(self):
        query = select(Mouth).where(Mouth.is_active.is_(True))
        result = await self.session.execute(query)

        return result.scalars().first()
