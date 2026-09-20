from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import CooperativeAccessGrant
from app.domain.repositories import CooperativeAccessGrantRepository
from app.infrastructure.models import CooperativeAccessGrantModel


def _to_entity(model: CooperativeAccessGrantModel) -> CooperativeAccessGrant:
    return CooperativeAccessGrant(
        id=model.id,
        user_id=model.user_id,
        cooperative_id=model.cooperative_id,
        granted_by=model.granted_by,
        created_at=model.created_at,
    )


class SqlAlchemyCooperativeAccessGrantRepository(CooperativeAccessGrantRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_cooperative_ids_for(self, user_id: UUID) -> list[UUID]:
        result = await self._session.execute(
            select(CooperativeAccessGrantModel.cooperative_id).where(CooperativeAccessGrantModel.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(self, *, user_id: UUID, cooperative_id: UUID, granted_by: UUID) -> CooperativeAccessGrant:
        model = CooperativeAccessGrantModel(user_id=user_id, cooperative_id=cooperative_id, granted_by=granted_by)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, grant_id: UUID) -> bool:
        model = await self._session.get(CooperativeAccessGrantModel, grant_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    async def list_for_cooperative(self, cooperative_id: UUID) -> list[CooperativeAccessGrant]:
        result = await self._session.execute(
            select(CooperativeAccessGrantModel).where(CooperativeAccessGrantModel.cooperative_id == cooperative_id)
        )
        return [_to_entity(m) for m in result.scalars().all()]
