from sqlalchemy.ext.asyncio import AsyncSession


class BaseDataBaseRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
