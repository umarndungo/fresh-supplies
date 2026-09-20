from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import OwnerType
from app.domain.repositories import TenantUsageRepository
from app.infrastructure.models import CooperativeModel, ProduceModel, ShipmentModel, UserModel


class SqlAlchemyTenantUsageRepository(TenantUsageRepository):
    """Deliberately narrow: every query here is a COUNT/SUM aggregate scoped
    by cooperative_id, never a row select — see
    backend/docs/multitenancy_design.md §7.2/§7.3. This is what makes "sees
    usage, not internal data" a structural guarantee for ADMINISTRATOR rather
    than a filtered view of the same query a tenant uses."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def _usage_for(self, cooperative_id: UUID) -> dict:
        member_count = await self._session.scalar(
            select(func.count()).select_from(UserModel).where(UserModel.cooperative_id == cooperative_id)
        )
        shipment_count = await self._session.scalar(
            select(func.count())
            .select_from(ShipmentModel)
            .where(ShipmentModel.owner_type == OwnerType.COOPERATIVE, ShipmentModel.cooperative_id == cooperative_id)
        )
        produce_item_count = await self._session.scalar(
            select(func.count())
            .select_from(ProduceModel)
            .where(ProduceModel.owner_type == OwnerType.COOPERATIVE, ProduceModel.cooperative_id == cooperative_id)
        )
        total_quantity_kg = await self._session.scalar(
            select(func.coalesce(func.sum(ProduceModel.quantity_kg), 0))
            .where(ProduceModel.owner_type == OwnerType.COOPERATIVE, ProduceModel.cooperative_id == cooperative_id)
        )
        return {
            "cooperative_id": cooperative_id,
            "member_count": member_count or 0,
            "shipment_count": shipment_count or 0,
            "produce_item_count": produce_item_count or 0,
            "total_quantity_kg": float(total_quantity_kg or 0),
        }

    async def get_cooperative_usage(self, cooperative_id: UUID) -> dict:
        return await self._usage_for(cooperative_id)

    async def list_cooperative_usage(self) -> list[dict]:
        cooperative_ids = (await self._session.execute(select(CooperativeModel.id))).scalars().all()
        return [await self._usage_for(cid) for cid in cooperative_ids]
