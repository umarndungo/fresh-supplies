from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities import ProduceItem, ProduceStatus, Shipment, ShipmentStatus, User, UserRole


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def create(
        self,
        *,
        email: str,
        full_name: str,
        hashed_password: str,
        role: UserRole,
        organization_name: str | None,
    ) -> User: ...


class ShipmentRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[Shipment]: ...

    @abstractmethod
    async def get_by_id(self, shipment_id: UUID) -> Shipment | None: ...

    @abstractmethod
    async def create(
        self,
        *,
        origin: str,
        destination: str,
        produce_type: str,
        status: ShipmentStatus,
        scheduled_date: datetime,
        delivery_date: datetime | None,
        created_by: UUID,
    ) -> Shipment: ...

    @abstractmethod
    async def update(
        self,
        shipment_id: UUID,
        *,
        status: ShipmentStatus | None = None,
        delivery_date: datetime | None = None,
    ) -> Shipment | None: ...

    @abstractmethod
    async def delete(self, shipment_id: UUID) -> bool: ...


class ProduceRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[ProduceItem]: ...

    @abstractmethod
    async def get_by_id(self, produce_id: UUID) -> ProduceItem | None: ...

    @abstractmethod
    async def create(
        self,
        *,
        name: str,
        variety: str,
        quantity_kg: float,
        unit_price: float,
        quality_grade: str,
        harvest_date: datetime,
        storage_location: str,
        cooperative_id: UUID,
        status: ProduceStatus,
    ) -> ProduceItem: ...

    @abstractmethod
    async def update(
        self,
        produce_id: UUID,
        *,
        name: str | None = None,
        variety: str | None = None,
        quantity_kg: float | None = None,
        unit_price: float | None = None,
        quality_grade: str | None = None,
        harvest_date: datetime | None = None,
        storage_location: str | None = None,
        status: ProduceStatus | None = None,
    ) -> ProduceItem | None: ...

    @abstractmethod
    async def delete(self, produce_id: UUID) -> bool: ...
