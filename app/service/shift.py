from db.models import Shift
from db.repository.shift import ShiftRepository
from service.base import BaseService


class ShiftService(BaseService):
    def __init__(self, shift_repository: ShiftRepository) -> None:
        self._shift_repository = shift_repository

    async def begin_shift(self, telegram_id: int, month_id: int, rate: int) -> None:
        await self._shift_repository.create(
            telegram_id=telegram_id, month_id=month_id, rate=rate
        )

    async def get_active_shift(self, telegram_id: int) -> Shift | None:
        return await self._shift_repository.get_active_shift(telegram_id=telegram_id)
