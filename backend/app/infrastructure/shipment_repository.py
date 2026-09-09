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
        origin_latitude=model.origin_latitude,
        origin_longitude=model.origin_longitude,
        destination_latitude=model.destination_latitude,
        destination_longitude=model.destination_longitude,
        temperature_c=model.temperature_c,
        transit_duration_hr=model.transit_duration_hr,
        pressure_psi=model.pressure_psi,
        baseline_loss_pct=model.baseline_loss_pct,
        quantity_kg=model.quantity_kg,
        spoilage_probability=model.spoilage_probability,
        risk_tier=model.risk_tier,
        spoil_prediction=model.spoil_prediction,
        market_recommendations=model.market_recommendations,
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
        # Origin location (source)
        origin_latitude: float | None = None,
        origin_longitude: float | None = None,
        # Destination location (market)
        destination_latitude: float | None = None,
        destination_longitude: float | None = None,
        # ML prediction fields (optional)
        temperature_c: float | None = None,
        transit_duration_hr: float | None = None,
        pressure_psi: float | None = None,
        baseline_loss_pct: float | None = None,
        quantity_kg: float | None = None,
    ) -> Shipment:
        model = ShipmentModel(
            origin=origin,
            destination=destination,
            produce_type=produce_type,
            status=status,
            scheduled_date=scheduled_date,
            delivery_date=delivery_date,
            created_by=created_by,
            origin_latitude=origin_latitude,
            origin_longitude=origin_longitude,
            destination_latitude=destination_latitude,
            destination_longitude=destination_longitude,
            temperature_c=temperature_c,
            transit_duration_hr=transit_duration_hr,
            pressure_psi=pressure_psi,
            baseline_loss_pct=baseline_loss_pct,
            quantity_kg=quantity_kg,
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
        spoilage_probability: float | None = None,
        risk_tier: str | None = None,
        spoil_prediction: bool | None = None,
        market_recommendations: list[dict] | None = None,
    ) -> Shipment | None:
        model = await self._session.get(ShipmentModel, shipment_id)
        if not model:
            return None
        if status is not None:
            model.status = status
        if delivery_date is not None:
            model.delivery_date = delivery_date
        if spoilage_probability is not None:
            model.spoilage_probability = spoilage_probability
        if risk_tier is not None:
            model.risk_tier = risk_tier
        if spoil_prediction is not None:
            model.spoil_prediction = spoil_prediction
        if market_recommendations is not None:
            model.market_recommendations = market_recommendations
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
