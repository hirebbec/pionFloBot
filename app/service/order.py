from db.repository.order import OrderRepository
from service.base import BaseService
from sqlalchemy.orm import Mapped


class OrderService(BaseService):
    def __init__(self, order_repository: OrderRepository) -> None:
        self._order_repository = order_repository

    async def create_order(self, shift_id: Mapped[int], amount: int) -> None:
        await self._order_repository.create(shift_id=shift_id, amount=amount)
