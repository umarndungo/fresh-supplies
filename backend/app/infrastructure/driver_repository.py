from datetime import datetime
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import DriverRepository
from app.infrastructure.models import ShipmentModel


class SqlAlchemyDriverRepository(DriverRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_manifest_stops(self, date: datetime, user_id: UUID, user_role: str) -> list[dict]:
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        query = select(ShipmentModel).where(
            and_(
                ShipmentModel.scheduled_date >= date_start,
                ShipmentModel.scheduled_date <= date_end,
                ShipmentModel.status.in_(["SCHEDULED", "IN_TRANSIT"]),
            )
        )

        if user_role == "FARMER_COOPERATIVE":
            query = query.where(ShipmentModel.created_by == user_id)

        result = await self._session.execute(query.order_by(ShipmentModel.scheduled_date))
        shipments = result.scalars().all()

        stops = []
        for i, s in enumerate(shipments):
            stops.append({
                "shipment_id": s.id,
                "owner_type": s.owner_type.value if s.owner_type else "INDIVIDUAL",
                "cooperative_name": None,
                "crop": s.produce_type,
                "quantity_kg": 0.0,
                "pickup_location": {"lat": 0.0, "lon": 0.0, "label": s.origin},
                "destination_market": s.destination,
                "risk_tier": "FRESH",
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
        }

    async def confirm_stop(self, shipment_id: UUID, confirmed_at: datetime, lat: float, lon: float) -> dict:
        model = await self._session.get(ShipmentModel, shipment_id)
        if not model:
            return {"status": "not_found"}
        if model.status != "SCHEDULED":
            return {"status": "already_confirmed", "shipment_status": model.status.value}
        model.status = "IN_TRANSIT"
        await self._session.commit()
        return {"status": "delivered", "shipment_status": "IN_TRANSIT"}
