from uuid import UUID

from app.core.exceptions import ForbiddenError, NotFoundError
from app.domain.entities import CommodityClass, ProduceItem, ProduceStatus, User, UserRole
from app.domain.repositories import ProduceRepository


_MANAGE_ROLES = {UserRole.ADMINISTRATOR, UserRole.FARMER_COOPERATIVE}


class ProduceService:
    def __init__(self, produce_repository: ProduceRepository):
        self._produce = produce_repository

    async def list_produce(self) -> list[ProduceItem]:
        return await self._produce.list_all()

    async def get_produce(self, produce_id: UUID) -> ProduceItem:
        produce = await self._produce.get_by_id(produce_id)
        if not produce:
            raise NotFoundError("Produce item not found.")
        return produce

    async def create_produce(
        self,
        *,
        actor: User,
        name: str,
        variety: str,
        quantity_kg: float,
        unit_price: float,
        quality_grade: str,
        harvest_date,
        storage_location: str,
        commodity_class: CommodityClass = CommodityClass.PERISHABLE,
    ) -> ProduceItem:
        self._ensure_can_manage(actor)
        return await self._produce.create(
            name=name,
            variety=variety,
            quantity_kg=quantity_kg,
            unit_price=unit_price,
            quality_grade=quality_grade,
            harvest_date=harvest_date,
            storage_location=storage_location,
            commodity_class=commodity_class,
            cooperative_id=actor.id,
            status=ProduceStatus.AVAILABLE,
        )

    async def update_produce(
        self,
        produce_id: UUID,
        *,
        actor: User,
        name: str | None = None,
        variety: str | None = None,
        quantity_kg: float | None = None,
        unit_price: float | None = None,
        quality_grade: str | None = None,
        harvest_date=None,
        storage_location: str | None = None,
        commodity_class: CommodityClass | None = None,
        status: ProduceStatus | None = None,
    ) -> ProduceItem:
        self._ensure_can_manage(actor)
        updated = await self._produce.update(
            produce_id,
            name=name,
            variety=variety,
            quantity_kg=quantity_kg,
            unit_price=unit_price,
            quality_grade=quality_grade,
            harvest_date=harvest_date,
            storage_location=storage_location,
            commodity_class=commodity_class,
            status=status,
        )
        if not updated:
            raise NotFoundError("Produce item not found.")
        return updated

    async def delete_produce(self, produce_id: UUID, *, actor: User) -> None:
        self._ensure_can_manage(actor)
        deleted = await self._produce.delete(produce_id)
        if not deleted:
            raise NotFoundError("Produce item not found.")

    def _ensure_can_manage(self, actor: User) -> None:
        if actor.role not in _MANAGE_ROLES:
            raise ForbiddenError("Only administrators and farmer cooperatives can manage produce inventory.")