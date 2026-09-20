"""Shared tenant-visibility scoping for ShipmentService / ProduceService /
DriverService.

See backend/docs/multitenancy_design.md §4. A VisibilityScope says which
records an actor may see: their own solo ("individual") records, records
belonging to one or more cooperatives (their own, for a FARMER_COOPERATIVE;
every cooperative they've been explicitly granted, for
LOGISTICS_MANAGER/MARKET_ANALYST), or — for DRIVER — shipments specifically
assigned to them (driver_user_id), independent of which cooperative those
shipments belong to. A driver doesn't get cooperative-wide visibility just
because they're hauling one shipment for that cooperative.

ADMINISTRATOR deliberately has no case here — it's refused at the top of
every ShipmentService/ProduceService/DriverService read/mutate method (see
require_not_administrator) before scope_for is ever called, so there is no
branch here that could silently start returning "sees everything" if this
function is edited later without noticing the omission was load-bearing.
"""

from dataclasses import dataclass, field
from uuid import UUID

from app.core.exceptions import ForbiddenError
from app.domain.entities import OwnerType, User, UserRole
from app.domain.repositories import CooperativeAccessGrantRepository

_GRANT_BASED_ROLES = (UserRole.LOGISTICS_MANAGER, UserRole.MARKET_ANALYST)


@dataclass(frozen=True)
class VisibilityScope:
    cooperative_ids: frozenset[UUID] = field(default_factory=frozenset)
    own_user_id: UUID | None = None
    assigned_driver_id: UUID | None = None

    def covers(
        self,
        *,
        owner_type: OwnerType,
        cooperative_id: UUID | None,
        created_by: UUID,
        driver_user_id: UUID | None = None,
    ) -> bool:
        if self.assigned_driver_id is not None and driver_user_id == self.assigned_driver_id:
            return True
        if owner_type == OwnerType.INDIVIDUAL:
            return self.own_user_id is not None and created_by == self.own_user_id
        return cooperative_id is not None and cooperative_id in self.cooperative_ids


async def scope_for(actor: User, grants: CooperativeAccessGrantRepository) -> VisibilityScope:
    if actor.role == UserRole.DRIVER:
        # A driver sees exactly the shipments assigned to them — not their
        # cooperative's whole pool, even if they belong to one.
        return VisibilityScope(assigned_driver_id=actor.id)

    if actor.role in _GRANT_BASED_ROLES:
        granted = await grants.list_cooperative_ids_for(actor.id)
        return VisibilityScope(cooperative_ids=frozenset(granted))  # empty = sees nothing, not everything

    # FARMER_COOPERATIVE (the only other role that ever reaches here).
    if actor.cooperative_id is not None:
        return VisibilityScope(cooperative_ids=frozenset({actor.cooperative_id}))
    return VisibilityScope(own_user_id=actor.id)


def require_not_administrator(actor: User) -> None:
    """ADMINISTRATOR manages tenants and sees aggregate billing usage (see
    AdminTenantService) — it never reads or writes a shipment/produce row's
    content. This is the structural half of that rule; the other half is
    that scope_for() above has no ADMINISTRATOR branch at all."""
    if actor.role == UserRole.ADMINISTRATOR:
        raise ForbiddenError(
            "Administrators manage tenants and billing usage, not individual shipment/produce records."
        )
