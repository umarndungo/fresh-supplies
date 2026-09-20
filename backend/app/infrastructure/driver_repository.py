from datetime import datetime
from typing import Iterable
from uuid import UUID

from sqlalchemy import and_, false, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import OwnerType, ShipmentStatus
from app.domain.repositories import DriverRepository
from app.infrastructure.models import ShipmentModel


class SqlAlchemyDriverRepository(DriverRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_manifest_stops(
        self,
        date: datetime,
        *,
        owner_id: UUID | None = None,
        cooperative_ids: Iterable[UUID] | None = None,
        driver_user_id: UUID | None = None,
    ) -> list[dict]:
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        query = select(ShipmentModel).where(
            and_(
                ShipmentModel.scheduled_date >= date_start,
                ShipmentModel.scheduled_date <= date_end,
                ShipmentModel.status.in_([ShipmentStatus.SCHEDULED, ShipmentStatus.IN_TRANSIT]),
            )
        )

        # Tenant scoping (backend/docs/multitenancy_design.md §4, extended for
        # DRIVER in tenancy.VisibilityScope) — same shape as
        # ShipmentRepository.list_all. Passing none of owner_id/
        # cooperative_ids/driver_user_id means "no scoping"; DriverService
        # always passes at least one (ADMINISTRATOR is refused before this
        # is ever reached).
        cooperative_ids = list(cooperative_ids) if cooperative_ids is not None else None
        conditions = []
        if owner_id is not None:
            conditions.append(and_(ShipmentModel.owner_type == OwnerType.INDIVIDUAL, ShipmentModel.created_by == owner_id))
        if cooperative_ids:
            conditions.append(
                and_(ShipmentModel.owner_type == OwnerType.COOPERATIVE, ShipmentModel.cooperative_id.in_(cooperative_ids))
            )
        if driver_user_id is not None:
            conditions.append(ShipmentModel.driver_user_id == driver_user_id)
        query = query.where(or_(*conditions)) if conditions else query.where(false())

        result = await self._session.execute(query.order_by(ShipmentModel.scheduled_date))
        shipments = result.scalars().all()

        stops = []
        for i, s in enumerate(shipments):
            stops.append({
                "shipment_id": s.id,
                "owner_type": s.owner_type.value if s.owner_type else "INDIVIDUAL",
                "cooperative_name": None,
                "crop": s.produce_type,
                "quantity_kg": float(s.quantity_kg) if s.quantity_kg is not None else 0.0,
                "pickup_location": {
                    "lat": s.origin_latitude or 0.0,
                    "lon": s.origin_longitude or 0.0,
                    "label": s.origin,
                },
                "destination_market": s.destination,
                "risk_tier": s.risk_tier or "FRESH",
                "sequence": i + 1,
            })
        return stops

    async def get_shipment_by_id(self, shipment_id: UUID) -> dict | None:
        model = await self._session.get(ShipmentModel, shipment_id)
        if not model:
            return None
        return {
            "id": model.id,
            "status": model.status.value,
            "owner_type": model.owner_type or OwnerType.INDIVIDUAL,
            "cooperative_id": model.cooperative_id,
            "created_by": model.created_by,
            "driver_user_id": model.driver_user_id,
        }

    async def confirm_stop(self, shipment_id: UUID, confirmed_at: datetime, lat: float, lon: float) -> dict:
        model = await self._session.get(ShipmentModel, shipment_id)
        if not model:
            return {"status": "not_found"}
        if model.status != ShipmentStatus.SCHEDULED:
            return {"status": "already_confirmed", "shipment_status": model.status.value}
        model.status = ShipmentStatus.IN_TRANSIT
        await self._session.commit()
        return {"status": "confirmed", "shipment_status": "IN_TRANSIT"}
