from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Cooperative
from app.domain.repositories import CooperativeRepository
from app.infrastructure.models import CooperativeModel


def _to_entity(model: CooperativeModel) -> Cooperative:
    return Cooperative(
        id=model.id,
        name=model.name,
        created_by=model.created_by,
        created_at=model.created_at,
    )


class SqlAlchemyCooperativeRepository(CooperativeRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, cooperative_id: UUID) -> Cooperative | None:
        model = await self._session.get(CooperativeModel, cooperative_id)
        return _to_entity(model) if model else None

    async def create(self, *, name: str, created_by: UUID) -> Cooperative:
        model = CooperativeModel(
            name=name,
            created_by=created_by,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def list_all(self) -> list[Cooperative]:
        result = await self._session.execute(select(CooperativeModel).order_by(CooperativeModel.created_at.desc()))
        return [_to_entity(m) for m in result.scalars().all()]

    async def update(self, cooperative_id: UUID, *, name: str | None = None) -> Cooperative | None:
        model = await self._session.get(CooperativeModel, cooperative_id)
        if not model:
            return None
        if name is not None:
            model.name = name
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)
