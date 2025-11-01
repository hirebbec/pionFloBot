from typing import Sequence

from db.models import Order
from db.repository.order import OrderRepository
from utils.schemas import StatSchema
from service.base import BaseService


class OrderService(BaseService):
    def __init__(self, order_repository: OrderRepository) -> None:
        self._order_repository = order_repository

    async def create_order(self, shift_id: int, amount: int) -> None:
        await self._order_repository.create(shift_id=shift_id, amount=amount)

    async def get_orders_stat_by_shift_id(self, shift_id: int) -> StatSchema:
        orders = await self._order_repository.get_by_shift_id(shift_id=shift_id)

        return StatSchema(
            count=len(orders), total=sum([order.amount for order in orders])
        )

    async def get_orders_by_shift_id(self, shift_id: int) -> Sequence[Order]:
        return await self._order_repository.get_by_shift_id(shift_id=shift_id)
