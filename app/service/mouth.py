from db.repository.mouth import MouthRepository
from service.base import BaseService


class MouthService(BaseService):
    def __init__(self, mouth_repository: MouthRepository) -> None:
        self._mouth_repository = mouth_repository

    async def begin_mouth(self, telegram_id: str) -> str:
        if await self._mouth_repository.get_active_mouth(telegram_id=telegram_id):
            return "Чтобы начать текущий месяц, необходимо завершить текущий месяц."

        await self._mouth_repository.create(telegram_id=telegram_id)

        return "Новый месяц начат!"
