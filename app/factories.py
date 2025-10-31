from db.repository.mouth import MouthRepository
from db.repository.user import UserRepository
from db.session import get_async_session
from service.mouth import MouthService
from service.user import UserService


def build_services() -> dict:
    async_session_maker = get_async_session()

    async def user_service_factory():
        async with async_session_maker() as session:
            user_repository = UserRepository(session=session)
            return UserService(user_repository=user_repository)

    async def mouth_service_factory():
        async with async_session_maker() as session:
            mouth_repository = MouthRepository(session=session)
            return MouthService(mouth_repository=mouth_repository)

    return {
        "user_service_factory": user_service_factory,
        "mouth_service_factory": mouth_service_factory,
    }
