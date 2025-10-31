from db.models import User
from db.repository.user import UserRepository
from service.base import BaseService


class UserService(BaseService):
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def create_user(self, telegram_id: str) -> None:
        await self._user_repository.create(telegram_id=telegram_id)

    async def get_by_telegram_id(self, telegram_id: str) -> User | None:
        return await self._user_repository.get_by_telegram_id(telegram_id=telegram_id)
