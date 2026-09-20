from datetime import datetime
from uuid import UUID

from app.application.tenancy import require_not_administrator, scope_for
from app.core.exceptions import ForbiddenError, NotFoundError
from app.domain.entities import User
from app.domain.repositories import CooperativeAccessGrantRepository, DriverRepository


class DriverService:
    def __init__(self, driver_repository: DriverRepository, grants: CooperativeAccessGrantRepository):
        self._driver = driver_repository
        self._grants = grants

    async def get_manifest(self, date: datetime, *, actor: User) -> list[dict]:
        require_not_administrator(actor)
        scope = await scope_for(actor, self._grants)
        return await self._driver.get_manifest_stops(
            date,
            owner_id=scope.own_user_id,
            cooperative_ids=scope.cooperative_ids,
            driver_user_id=scope.assigned_driver_id,
        )

    async def confirm_stop(self, shipment_id: UUID, confirmed_at: datetime, lat: float, lon: float, *, actor: User) -> dict:
        require_not_administrator(actor)
        shipment = await self._driver.get_shipment_by_id(shipment_id)
        if not shipment:
            raise NotFoundError("Shipment not found.")
        scope = await scope_for(actor, self._grants)
        if not scope.covers(
            owner_type=shipment["owner_type"],
            cooperative_id=shipment["cooperative_id"],
            created_by=shipment["created_by"],
            driver_user_id=shipment["driver_user_id"],
        ):
            # Same response as "doesn't exist" — a 403 would confirm this
            # shipment ID is real but belongs to someone else.
            raise NotFoundError("Shipment not found.")

        result = await self._driver.confirm_stop(shipment_id, confirmed_at, lat, lon)
        if result.get("status") == "not_found":
            raise NotFoundError("Shipment not found.")
        return result
