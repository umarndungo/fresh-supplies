from uuid import UUID

from app.application.tenancy import require_not_administrator, scope_for
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.domain.entities import OwnerType, Shipment, ShipmentStatus, User, UserRole
from app.domain.repositories import (
    CooperativeAccessGrantRepository,
    ProduceRepository,
    ShipmentRepository,
    UserRepository,
)

# ADMINISTRATOR is deliberately absent — see tenancy.require_not_administrator
# and backend/docs/multitenancy_design.md §1/§7. LOGISTICS_MANAGER keeps
# mutate rights (status updates, rerouting) but only within cooperatives it
# has been explicitly granted (§4) — this is checked in _ensure_can_mutate,
# not by role alone.
_MANAGE_ROLES = {UserRole.LOGISTICS_MANAGER}


class ShipmentService:
    def __init__(
        self,
        shipment_repository: ShipmentRepository,
        grants: CooperativeAccessGrantRepository,
        users: UserRepository,
        produce: ProduceRepository,
    ):
        self._shipments = shipment_repository
        self._grants = grants
        self._users = users
        self._produce = produce

    async def list_shipments(self, *, actor: User) -> list[Shipment]:
        require_not_administrator(actor)
        scope = await scope_for(actor, self._grants)
        return await self._shipments.list_all(
            owner_id=scope.own_user_id,
            cooperative_ids=scope.cooperative_ids,
            driver_user_id=scope.assigned_driver_id,
        )

    async def get_shipment(self, shipment_id: UUID, *, actor: User) -> Shipment:
        require_not_administrator(actor)
        shipment = await self._shipments.get_by_id(shipment_id)
        scope = await scope_for(actor, self._grants)
        if not shipment or not scope.covers(
            owner_type=shipment.owner_type,
            cooperative_id=shipment.cooperative_id,
            created_by=shipment.created_by,
            driver_user_id=shipment.driver_user_id,
        ):
            # Same response whether the shipment doesn't exist or belongs to
            # another tenant — a 403 would confirm the ID is real.
            raise NotFoundError("Shipment not found.")
        return shipment

    async def create_shipment(
        self,
        *,
        actor: User,
        origin: str,
        destination: str,
        produce_type: str,
        scheduled_date,
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
        produce_id=None,
        harvest_date_snapshot=None,
        storage_spoilage_probability_snapshot: float | None = None,
        estimated_shelf_life_days_snapshot: float | None = None,
        storage_temperature_c_snapshot: float | None = None,
        storage_pressure_psi_snapshot: float | None = None,
    ) -> Shipment:
        self._ensure_can_manage(actor)
        owner_type, cooperative_id = await self._resolve_shipment_tenancy(actor, produce_id)
        return await self._shipments.create(
            origin=origin,
            destination=destination,
            produce_type=produce_type,
            status=ShipmentStatus.SCHEDULED,
            scheduled_date=scheduled_date,
            delivery_date=None,
            created_by=actor.id,
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

    async def update_shipment(
        self,
        shipment_id: UUID,
        *,
        actor: User,
        status: ShipmentStatus | None = None,
        delivery_date=None,
        spoilage_probability: float | None = None,
        risk_tier: str | None = None,
        spoil_prediction: bool | None = None,
        market_recommendations: list[dict] | None = None,
        produce_id=None,
        harvest_date_snapshot=None,
        storage_spoilage_probability_snapshot: float | None = None,
        estimated_shelf_life_days_snapshot: float | None = None,
        storage_temperature_c_snapshot: float | None = None,
        storage_pressure_psi_snapshot: float | None = None,
    ) -> Shipment:
        self._ensure_can_manage(actor)
        await self._ensure_can_mutate(shipment_id, actor)
        updated = await self._shipments.update(
            shipment_id,
            status=status,
            delivery_date=delivery_date,
            spoilage_probability=spoilage_probability,
            risk_tier=risk_tier,
            spoil_prediction=spoil_prediction,
            market_recommendations=market_recommendations,
            produce_id=produce_id,
            harvest_date_snapshot=harvest_date_snapshot,
            storage_spoilage_probability_snapshot=storage_spoilage_probability_snapshot,
            estimated_shelf_life_days_snapshot=estimated_shelf_life_days_snapshot,
            storage_temperature_c_snapshot=storage_temperature_c_snapshot,
            storage_pressure_psi_snapshot=storage_pressure_psi_snapshot,
        )
        if not updated:
            raise NotFoundError("Shipment not found.")
        return updated

    async def delete_shipment(self, shipment_id: UUID, *, actor: User) -> None:
        self._ensure_can_manage(actor)
        await self._ensure_can_mutate(shipment_id, actor)
        deleted = await self._shipments.delete(shipment_id)
        if not deleted:
            raise NotFoundError("Shipment not found.")

    async def assign_driver(self, shipment_id: UUID, *, actor: User, driver_user_id: UUID) -> Shipment:
        """Phase 2 (driver assignment). Only a LOGISTICS_MANAGER with scope
        over this shipment's cooperative can assign a driver, and only to a
        real DRIVER account — one belonging to the same cooperative when the
        shipment is cooperative-owned (an individual/solo shipment has no
        cooperative to match against, so any in-scope driver is acceptable).
        See backend/docs/multitenancy_design.md Phase 2."""
        self._ensure_can_manage(actor)
        shipment = await self._ensure_can_mutate(shipment_id, actor)

        driver = await self._users.get_by_id(driver_user_id)
        if not driver or driver.role != UserRole.DRIVER:
            raise ValidationError("driver_user_id must reference an existing DRIVER account.")
        if (
            shipment.owner_type == OwnerType.COOPERATIVE
            and driver.cooperative_id is not None
            and driver.cooperative_id != shipment.cooperative_id
        ):
            raise ValidationError("This driver belongs to a different cooperative than the shipment.")

        updated = await self._shipments.update(shipment_id, driver_user_id=driver_user_id)
        if not updated:
            raise NotFoundError("Shipment not found.")
        return updated

    async def _resolve_shipment_tenancy(
        self, actor: User, produce_id: UUID | None
    ) -> tuple[OwnerType, UUID | None]:
        # LOGISTICS_MANAGER (the only role that reaches this method — see
        # _ensure_can_manage) has no personal tenancy of its own: account_type
        # and cooperative_id are farmer concepts and are meaningless (usually
        # None) on a staff account. Deriving owner_type/cooperative_id from
        # actor.account_type here, as this used to, mints a shipment nobody
        # can ever see again — a manager's own visibility scope is always
        # grant-based (never own_user_id), so an INDIVIDUAL-owned shipment
        # "created_by" a manager is invisible even to that same manager.
        # The correct source of truth is the produce lot being shipped, when
        # one is given — it already carries real tenancy set by the farmer
        # who logged it (ProduceService.create_produce).
        if produce_id is not None:
            produce = await self._produce.get_by_id(produce_id)
            if not produce:
                raise NotFoundError("Produce lot not found.")
            scope = await scope_for(actor, self._grants)
            if not scope.covers(
                owner_type=produce.owner_type, cooperative_id=produce.cooperative_id, created_by=produce.created_by
            ):
                # Same "not found" framing as everywhere else in this file —
                # a manager with no grant over this produce's cooperative
                # can't use it to smuggle a shipment into that tenant.
                raise NotFoundError("Produce lot not found.")
            return produce.owner_type, produce.cooperative_id

        return (OwnerType(actor.account_type.value) if actor.account_type else OwnerType.INDIVIDUAL), actor.cooperative_id

    def _ensure_can_manage(self, actor: User) -> None:
        if actor.role not in _MANAGE_ROLES:
            raise ForbiddenError("Only logistics managers can manage shipments.")

    async def _ensure_can_mutate(self, shipment_id: UUID, actor: User) -> Shipment:
        # actor.role == LOGISTICS_MANAGER is already guaranteed by
        # _ensure_can_manage; this narrows further to "within a cooperative
        # this manager has been granted" (backend/docs/multitenancy_design.md
        # §4) instead of "any shipment, unscoped." Returns the shipment so
        # callers (e.g. assign_driver) that need it after the check don't
        # have to fetch it twice.
        shipment = await self._shipments.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundError("Shipment not found.")
        scope = await scope_for(actor, self._grants)
        if not scope.covers(
            owner_type=shipment.owner_type,
            cooperative_id=shipment.cooperative_id,
            created_by=shipment.created_by,
            driver_user_id=shipment.driver_user_id,
        ):
            raise NotFoundError("Shipment not found.")
        return shipment
