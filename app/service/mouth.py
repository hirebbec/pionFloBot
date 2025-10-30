from db.repository.mouth import MouthRepository
from service.base import BaseService


class MouthService(BaseService):
    def __init__(self, mouth_repository: MouthRepository):
        self.mouth_repository = mouth_repository

    async def create_mouth(self):
        self.mouth_repository.create()
