from db.repository.month import MonthRepository
from db.repository.user import UserRepository
from db.session import get_async_session
from service.month import MonthService
from service.user import UserService


def build_services() -> dict:
    async_session_maker = get_async_session()

    async def user_service_factory():
        async with async_session_maker() as session:
            user_repository = UserRepository(session=session)
            return UserService(user_repository=user_repository)

    async def month_service_factory():
        async with async_session_maker() as session:
            month_repository = MonthRepository(session=session)
            return MonthService(month_repository=month_repository)

    return {
        "user_service_factory": user_service_factory,
        "month_service_factory": month_service_factory,
    }
