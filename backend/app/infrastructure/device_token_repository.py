from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import DeviceTokenRepository
from app.infrastructure.models import DeviceTokenModel


class SqlAlchemyDeviceTokenRepository(DeviceTokenRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def register(self, *, user_id: UUID, device_token: str, platform: str) -> None:
        existing = await self._session.execute(
            select(DeviceTokenModel).where(
                DeviceTokenModel.user_id == user_id,
                DeviceTokenModel.device_token == device_token,
            )
        )
        if existing.scalar_one_or_none():
            return
        model = DeviceTokenModel(
            user_id=user_id,
            device_token=device_token,
            platform=platform,
        )
        self._session.add(model)
        await self._session.commit()

    async def get_tokens_for_user(self, user_id: UUID) -> list[str]:
        result = await self._session.execute(
            select(DeviceTokenModel.device_token).where(DeviceTokenModel.user_id == user_id)
        )
        return [row[0] for row in result.all()]
