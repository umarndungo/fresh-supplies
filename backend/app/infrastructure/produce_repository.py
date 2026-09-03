from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import CommodityClass, ProduceItem, ProduceStatus
from app.domain.repositories import ProduceRepository
from app.infrastructure.models import ProduceModel


def _to_entity(model: ProduceModel) -> ProduceItem:
    return ProduceItem(
        id=model.id,
        name=model.name,
        variety=model.variety,
        quantity_kg=float(model.quantity_kg),
        unit_price=float(model.unit_price),
        quality_grade=model.quality_grade,
        harvest_date=model.harvest_date,
        storage_location=model.storage_location,
        commodity_class=model.commodity_class,
        cooperative_id=model.cooperative_id,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyProduceRepository(ProduceRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_all(self) -> list[ProduceItem]:
        result = await self._session.execute(select(ProduceModel).order_by(ProduceModel.created_at.desc()))
        return [_to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, produce_id: UUID) -> ProduceItem | None:
        model = await self._session.get(ProduceModel, produce_id)
        return _to_entity(model) if model else None

    async def create(
        self,
        *,
        name: str,
        variety: str,
        quantity_kg: float,
        unit_price: float,
        quality_grade: str,
        harvest_date,
        storage_location: str,
        commodity_class: CommodityClass,
        cooperative_id: UUID,
        status: ProduceStatus,
    ) -> ProduceItem:
        model = ProduceModel(
            name=name,
            variety=variety,
            quantity_kg=quantity_kg,
            unit_price=unit_price,
            quality_grade=quality_grade,
            harvest_date=harvest_date,
            storage_location=storage_location,
            commodity_class=commodity_class,
            cooperative_id=cooperative_id,
            status=status,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(
        self,
        produce_id: UUID,
        *,
        name: str | None = None,
        variety: str | None = None,
        quantity_kg: float | None = None,
        unit_price: float | None = None,
        quality_grade: str | None = None,
        harvest_date=None,
        storage_location: str | None = None,
        commodity_class: CommodityClass | None = None,
        status: ProduceStatus | None = None,
    ) -> ProduceItem | None:
        model = await self._session.get(ProduceModel, produce_id)
        if not model:
            return None
        if name is not None:
            model.name = name
        if variety is not None:
            model.variety = variety
        if quantity_kg is not None:
            model.quantity_kg = quantity_kg
        if unit_price is not None:
            model.unit_price = unit_price
        if quality_grade is not None:
            model.quality_grade = quality_grade
        if harvest_date is not None:
            model.harvest_date = harvest_date
        if storage_location is not None:
            model.storage_location = storage_location
        if commodity_class is not None:
            model.commodity_class = commodity_class
        if status is not None:
            model.status = status
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, produce_id: UUID) -> bool:
        model = await self._session.get(ProduceModel, produce_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True