from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Shipment, ShipmentStatus
from app.domain.repositories import ShipmentRepository
from app.infrastructure.models import ShipmentModel


def _to_entity(model: ShipmentModel) -> Shipment:
    return Shipment(
        id=model.id,
        origin=model.origin,
        destination=model.destination,
        produce_type=model.produce_type,
        status=model.status,
        scheduled_date=model.scheduled_date,
        delivery_date=model.delivery_date,
        created_by=model.created_by,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyShipmentRepository(ShipmentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_all(self) -> list[Shipment]:
        result = await self._session.execute(select(ShipmentModel).order_by(ShipmentModel.scheduled_date.desc()))
        return [_to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, shipment_id: UUID) -> Shipment | None:
        model = await self._session.get(ShipmentModel, shipment_id)
        return _to_entity(model) if model else None

    async def create(
        self,
        *,
        origin,
        destination,
        produce_type,
        status,
        scheduled_date,
        delivery_date,
        created_by,
    ) -> Shipment:
        model = ShipmentModel(
            origin=origin,
            destination=destination,
            produce_type=produce_type,
            status=status,
            scheduled_date=scheduled_date,
            delivery_date=delivery_date,
            created_by=created_by,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(
        self,
        shipment_id: UUID,
        *,
        status: ShipmentStatus | None = None,
        delivery_date=None,
    ) -> Shipment | None:
        model = await self._session.get(ShipmentModel, shipment_id)
        if not model:
            return None
        if status is not None:
            model.status = status
        if delivery_date is not None:
            model.delivery_date = delivery_date
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, shipment_id: UUID) -> bool:
        model = await self._session.get(ShipmentModel, shipment_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True
