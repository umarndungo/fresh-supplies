from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import (
    OwnerType,
    ReconciliationStatus,
    ShipmentSyncStaging,
)
from app.domain.repositories import ShipmentSyncStagingRepository
from app.infrastructure.models import ShipmentSyncStagingModel


def _to_entity(model: ShipmentSyncStagingModel) -> ShipmentSyncStaging:
    return ShipmentSyncStaging(
        id=model.id,
        client_id=model.client_id,
        crop=model.crop,
        quantity_kg=float(model.quantity_kg),
        captured_at=model.captured_at,
        location_lat=model.location_lat,
        location_lon=model.location_lon,
        photo_ref=model.photo_ref,
        photo_status=model.photo_status,
        notes=model.notes,
        owner_type=model.owner_type,
        cooperative_id=model.cooperative_id,
        submitted_by_user_id=model.submitted_by_user_id,
        sync_received_at=model.sync_received_at,
        reconciliation_status=model.reconciliation_status,
        reconciled_shipment_id=model.reconciled_shipment_id,
    )


class SqlAlchemyShipmentSyncStagingRepository(ShipmentSyncStagingRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_client_id(self, client_id: str) -> ShipmentSyncStaging | None:
        result = await self._session.execute(
            select(ShipmentSyncStagingModel).where(ShipmentSyncStagingModel.client_id == client_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create(self, **kwargs) -> ShipmentSyncStaging:
        model = ShipmentSyncStagingModel(**kwargs)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update_photo_ref(self, client_id: str, photo_ref: str) -> None:
        await self._session.execute(
            update(ShipmentSyncStagingModel)
            .where(ShipmentSyncStagingModel.client_id == client_id)
            .values(photo_ref=photo_ref, photo_status="uploaded")
        )
        await self._session.commit()

    async def list_since(
        self,
        since: datetime,
        user_id: UUID | None = None,
        cooperative_id: UUID | None = None,
    ) -> list[ShipmentSyncStaging]:
        stmt = select(ShipmentSyncStagingModel).where(
            ShipmentSyncStagingModel.sync_received_at > since
        )
        if user_id is not None:
            stmt = stmt.where(ShipmentSyncStagingModel.submitted_by_user_id == user_id)
        if cooperative_id is not None:
            stmt = stmt.where(ShipmentSyncStagingModel.cooperative_id == cooperative_id)
        stmt = stmt.order_by(ShipmentSyncStagingModel.sync_received_at.desc())
        result = await self._session.execute(stmt)
        return [_to_entity(m) for m in result.scalars().all()]

    async def list_pending_reconciliation(self, limit: int = 50) -> list[ShipmentSyncStaging]:
        result = await self._session.execute(
            select(ShipmentSyncStagingModel)
            .where(ShipmentSyncStagingModel.reconciliation_status == ReconciliationStatus.PENDING)
            .order_by(ShipmentSyncStagingModel.sync_received_at.asc())
            .limit(limit)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def mark_reconciled(self, staging_id: UUID, shipment_id: UUID) -> None:
        await self._session.execute(
            update(ShipmentSyncStagingModel)
            .where(ShipmentSyncStagingModel.id == staging_id)
            .values(
                reconciliation_status=ReconciliationStatus.RECONCILED,
                reconciled_shipment_id=shipment_id,
            )
        )

    async def mark_failed(self, staging_id: UUID) -> None:
        await self._session.execute(
            update(ShipmentSyncStagingModel)
            .where(ShipmentSyncStagingModel.id == staging_id)
            .values(reconciliation_status=ReconciliationStatus.FAILED)
        )
