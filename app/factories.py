from contextlib import asynccontextmanager

from db.repository.month import MonthRepository
from db.repository.shift import ShiftRepository
from db.repository.user import UserRepository
from db.session import get_async_session
from service.month import MonthService
from service.shift import ShiftService
from service.user import UserService


def build_services() -> dict:
    async_session_maker = get_async_session()

    @asynccontextmanager
    async def user_service_factory():
        async with async_session_maker() as session:
            user_repository = UserRepository(session=session)
            service = UserService(user_repository=user_repository)
            yield service

    @asynccontextmanager
    async def month_service_factory():
        async with async_session_maker() as session:
            month_repository = MonthRepository(session=session)
            service = MonthService(month_repository=month_repository)
            yield service

    @asynccontextmanager
    async def shift_service_factory():
        async with async_session_maker() as session:
            shift_repository = ShiftRepository(session=session)
            service = ShiftService(shift_repository=shift_repository)
            yield service

    return {
        "user_service_factory": user_service_factory,
        "month_service_factory": month_service_factory,
        "shift_service_factory": shift_service_factory,
    }
