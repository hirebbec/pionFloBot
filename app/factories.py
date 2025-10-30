from db.repository.mouth import MouthRepository
from db.session import get_async_session
from service.mouth import MouthService


def build_services() -> dict:
    async_session_maker = get_async_session()

    async def mouth_service_factory():
        async with async_session_maker() as session:
            mouth_repository = MouthRepository(session=session)
            return MouthService(mouth_repository=mouth_repository)

    return {
        "mouth_service_factory": mouth_service_factory,
    }
