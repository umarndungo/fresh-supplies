from uuid import UUID

from app.core.exceptions import ForbiddenError, NotFoundError
from app.domain.entities import Shipment, ShipmentStatus, User, UserRole
from app.domain.repositories import ShipmentRepository

_MANAGE_ROLES = {UserRole.ADMINISTRATOR, UserRole.LOGISTICS_MANAGER}


class ShipmentService:
    def __init__(self, shipment_repository: ShipmentRepository):
        self._shipments = shipment_repository

    async def list_shipments(self) -> list[Shipment]:
        return await self._shipments.list_all()

    async def get_shipment(self, shipment_id: UUID) -> Shipment:
        shipment = await self._shipments.get_by_id(shipment_id)
        if not shipment:
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
    ) -> Shipment:
        self._ensure_can_manage(actor)
        return await self._shipments.create(
            origin=origin,
            destination=destination,
            produce_type=produce_type,
            status=ShipmentStatus.SCHEDULED,
            scheduled_date=scheduled_date,
            delivery_date=None,
            created_by=actor.id,
        )

    async def update_shipment(
        self,
        shipment_id: UUID,
        *,
        actor: User,
        status: ShipmentStatus | None = None,
        delivery_date=None,
    ) -> Shipment:
        self._ensure_can_manage(actor)
        updated = await self._shipments.update(shipment_id, status=status, delivery_date=delivery_date)
        if not updated:
            raise NotFoundError("Shipment not found.")
        return updated

    async def delete_shipment(self, shipment_id: UUID, *, actor: User) -> None:
        self._ensure_can_manage(actor)
        deleted = await self._shipments.delete(shipment_id)
        if not deleted:
            raise NotFoundError("Shipment not found.")

    def _ensure_can_manage(self, actor: User) -> None:
        if actor.role not in _MANAGE_ROLES:
            raise ForbiddenError("Only administrators and logistics managers can manage shipments.")
