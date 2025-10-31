from db.repository.month import MonthRepository
from service.base import BaseService


class MonthService(BaseService):
    def __init__(self, month_repository: MonthRepository) -> None:
        self._month_repository = month_repository

    async def begin_month(self, telegram_id: int) -> str:
        if await self._month_repository.get_active_month(telegram_id=telegram_id):
            return "Чтобы начать месяц, необходимо завершить текущий месяц."

        await self._month_repository.create(telegram_id=telegram_id)

        return "Новый месяц начат!"

    async def end_month(self, telegram_id: int) -> str:
        if not await self._month_repository.get_active_month(telegram_id=telegram_id):
            return "Месяц еще не начат."

        await self._month_repository.end_month(telegram_id=telegram_id)

        return "Месяц завершен!"
