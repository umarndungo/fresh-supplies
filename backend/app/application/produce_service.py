from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.application.tenancy import require_not_administrator, scope_for
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.domain.entities import (
    CommodityClass,
    CooperativeRole,
    OwnerType,
    ProduceItem,
    ProduceStatus,
    User,
    UserRole,
)
from app.domain.repositories import CooperativeAccessGrantRepository, ProduceRepository

# ADMINISTRATOR is deliberately absent — see tenancy.require_not_administrator
# and backend/docs/multitenancy_design.md §1/§7. Only FARMER_COOPERATIVE
# manages produce; LOGISTICS_MANAGER/MARKET_ANALYST are read-only for produce
# (nothing in the design calls for either to write produce records).
_MANAGE_ROLES = {UserRole.FARMER_COOPERATIVE}


class ProduceService:
    def __init__(self, produce_repository: ProduceRepository, grants: CooperativeAccessGrantRepository):
        self._produce = produce_repository
        self._grants = grants

    async def list_produce(self, *, actor: User) -> list[ProduceItem]:
        require_not_administrator(actor)
        scope = await scope_for(actor, self._grants)
        return await self._produce.list_all(owner_id=scope.own_user_id, cooperative_ids=scope.cooperative_ids)

    async def get_produce(self, produce_id: UUID, *, actor: User) -> ProduceItem:
        require_not_administrator(actor)
        produce = await self._produce.get_by_id(produce_id)
        scope = await scope_for(actor, self._grants)
        if not produce or not scope.covers(
            owner_type=produce.owner_type, cooperative_id=produce.cooperative_id, created_by=produce.created_by
        ):
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
        storage_temperature_c: float | None = None,
        storage_pressure_psi: float | None = None,
    ) -> ProduceItem:
        self._ensure_can_manage(actor)
        owner_type = OwnerType(actor.account_type.value) if actor.account_type else OwnerType.INDIVIDUAL
        return await self._produce.create(
            name=name,
            variety=variety,
            quantity_kg=quantity_kg,
            unit_price=unit_price,
            quality_grade=quality_grade,
            harvest_date=harvest_date,
            storage_location=storage_location,
            commodity_class=commodity_class,
            created_by=actor.id,
            owner_type=owner_type,
            cooperative_id=actor.cooperative_id if owner_type == OwnerType.COOPERATIVE else None,
            status=ProduceStatus.AVAILABLE,
            storage_temperature_c=storage_temperature_c,
            storage_pressure_psi=storage_pressure_psi,
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
        storage_temperature_c: float | None = None,
        storage_pressure_psi: float | None = None,
        storage_spoilage_probability: float | None = None,
        storage_risk_tier: str | None = None,
        storage_spoil_prediction: bool | None = None,
        estimated_shelf_life_days: float | None = None,
    ) -> ProduceItem:
        self._ensure_can_manage(actor)
        await self._ensure_can_mutate(produce_id, actor)
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
            storage_temperature_c=storage_temperature_c,
            storage_pressure_psi=storage_pressure_psi,
            storage_spoilage_probability=storage_spoilage_probability,
            storage_risk_tier=storage_risk_tier,
            storage_spoil_prediction=storage_spoil_prediction,
            estimated_shelf_life_days=estimated_shelf_life_days,
        )
        if not updated:
            raise NotFoundError("Produce item not found.")
        return updated

    async def delete_produce(self, produce_id: UUID, *, actor: User) -> None:
        self._ensure_can_manage(actor)
        await self._ensure_can_mutate(produce_id, actor)
        try:
            deleted = await self._produce.delete(produce_id)
        except IntegrityError as exc:
            # shipments.produce_id -> produce.id has no ON DELETE clause
            # (RESTRICT by default), so a produce lot already linked to a
            # shipment can't just be removed out from under it.
            raise ConflictError("This produce item has been shipped and cannot be deleted.") from exc
        if not deleted:
            raise NotFoundError("Produce item not found.")

    def _ensure_can_manage(self, actor: User) -> None:
        if actor.role not in _MANAGE_ROLES:
            raise ForbiddenError("Only farmer cooperative accounts can manage produce inventory.")

    async def _ensure_can_mutate(self, produce_id: UUID, actor: User) -> None:
        # actor.role == FARMER_COOPERATIVE is already guaranteed by
        # _ensure_can_manage. Within that: the creator can always mutate
        # their own item; a cooperative ADMIN can mutate anything in their
        # own cooperative; a plain MEMBER can only mutate what they created
        # (backend/docs/multitenancy_design.md §1/§4).
        produce = await self._produce.get_by_id(produce_id)
        if not produce:
            raise NotFoundError("Produce item not found.")
        if produce.created_by == actor.id:
            return
        is_coop_admin = actor.cooperative_role == CooperativeRole.ADMIN
        same_cooperative = (
            produce.owner_type == OwnerType.COOPERATIVE
            and actor.cooperative_id is not None
            and produce.cooperative_id == actor.cooperative_id
        )
        if is_coop_admin and same_cooperative:
            return
        raise NotFoundError("Produce item not found.")
