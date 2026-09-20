from typing import Iterable
from uuid import UUID

from sqlalchemy import false, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import OwnerType, Shipment, ShipmentStatus
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
        cooperative_id=model.cooperative_id,
        # Pre-existing rows never had owner_type set on the web path; treat
        # unset the same as INDIVIDUAL rather than requiring a backfill.
        owner_type=model.owner_type or OwnerType.INDIVIDUAL,
        driver_user_id=model.driver_user_id,
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
        produce_id=model.produce_id,
        harvest_date_snapshot=model.harvest_date_snapshot,
        storage_spoilage_probability_snapshot=model.storage_spoilage_probability_snapshot,
        estimated_shelf_life_days_snapshot=model.estimated_shelf_life_days_snapshot,
        storage_temperature_c_snapshot=model.storage_temperature_c_snapshot,
        storage_pressure_psi_snapshot=model.storage_pressure_psi_snapshot,
    )


class SqlAlchemyShipmentRepository(ShipmentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_all(
        self,
        *,
        owner_id: UUID | None = None,
        cooperative_ids: Iterable[UUID] | None = None,
        driver_user_id: UUID | None = None,
    ) -> list[Shipment]:
        query = select(ShipmentModel).order_by(ShipmentModel.scheduled_date.desc())
        cooperative_ids = list(cooperative_ids) if cooperative_ids is not None else None
        if owner_id is not None or cooperative_ids is not None or driver_user_id is not None:
            # Tenant scoping (backend/docs/multitenancy_design.md §4): visible
            # iff created by owner_id (solo tenant), in one of the explicitly
            # passed cooperative_ids (own cooperative for a FARMER_COOPERATIVE
            # actor; every granted cooperative for LOGISTICS_MANAGER/
            # MARKET_ANALYST), or assigned to driver_user_id (a DRIVER sees
            # only what's assigned to them, regardless of cooperative).
            # Passing none of these means "no scoping" — callers must opt
            # into that explicitly, never by accident (there is no remaining
            # caller that does this for a real request; ADMINISTRATOR is
            # refused before reaching here).
            conditions = []
            if owner_id is not None:
                conditions.append(ShipmentModel.created_by == owner_id)
            if cooperative_ids:
                conditions.append(ShipmentModel.cooperative_id.in_(cooperative_ids))
            if driver_user_id is not None:
                conditions.append(ShipmentModel.driver_user_id == driver_user_id)
            query = query.where(or_(*conditions)) if conditions else query.where(false())
        result = await self._session.execute(query)
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
        owner_type: OwnerType = OwnerType.INDIVIDUAL,
        cooperative_id: UUID | None = None,
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
        produce_id: UUID | None = None,
        harvest_date_snapshot=None,
        storage_spoilage_probability_snapshot: float | None = None,
        estimated_shelf_life_days_snapshot: float | None = None,
        storage_temperature_c_snapshot: float | None = None,
        storage_pressure_psi_snapshot: float | None = None,
    ) -> Shipment:
        model = ShipmentModel(
            origin=origin,
            destination=destination,
            produce_type=produce_type,
            status=status,
            scheduled_date=scheduled_date,
            delivery_date=delivery_date,
            created_by=created_by,
            owner_type=owner_type,
            cooperative_id=cooperative_id,
            origin_latitude=origin_latitude,
            origin_longitude=origin_longitude,
            destination_latitude=destination_latitude,
            destination_longitude=destination_longitude,
            temperature_c=temperature_c,
            transit_duration_hr=transit_duration_hr,
            pressure_psi=pressure_psi,
            baseline_loss_pct=baseline_loss_pct,
            quantity_kg=quantity_kg,
            produce_id=produce_id,
            harvest_date_snapshot=harvest_date_snapshot,
            storage_spoilage_probability_snapshot=storage_spoilage_probability_snapshot,
            estimated_shelf_life_days_snapshot=estimated_shelf_life_days_snapshot,
            storage_temperature_c_snapshot=storage_temperature_c_snapshot,
            storage_pressure_psi_snapshot=storage_pressure_psi_snapshot,
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
        produce_id: UUID | None = None,
        harvest_date_snapshot=None,
        storage_spoilage_probability_snapshot: float | None = None,
        estimated_shelf_life_days_snapshot: float | None = None,
        storage_temperature_c_snapshot: float | None = None,
        storage_pressure_psi_snapshot: float | None = None,
        driver_user_id: UUID | None = None,
    ) -> Shipment | None:
        model = await self._session.get(ShipmentModel, shipment_id)
        if not model:
            return None
        if driver_user_id is not None:
            model.driver_user_id = driver_user_id
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
        if produce_id is not None:
            model.produce_id = produce_id
        if harvest_date_snapshot is not None:
            model.harvest_date_snapshot = harvest_date_snapshot
        if storage_spoilage_probability_snapshot is not None:
            model.storage_spoilage_probability_snapshot = storage_spoilage_probability_snapshot
        if estimated_shelf_life_days_snapshot is not None:
            model.estimated_shelf_life_days_snapshot = estimated_shelf_life_days_snapshot
        if storage_temperature_c_snapshot is not None:
            model.storage_temperature_c_snapshot = storage_temperature_c_snapshot
        if storage_pressure_psi_snapshot is not None:
            model.storage_pressure_psi_snapshot = storage_pressure_psi_snapshot
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
