from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities import (
    AccountType,
    Cooperative,
    OTPCode,
    ProduceItem,
    ProduceStatus,
    Shipment,
    ShipmentStatus,
    ShipmentSyncStaging,
    User,
    UserRole,
)


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

    @abstractmethod
    async def get_by_phone_number(self, phone_number: str) -> User | None: ...

    @abstractmethod
    async def create_phone_user(self, *, phone_number: str) -> User: ...

    @abstractmethod
    async def update_profile(
        self,
        user_id: UUID,
        *,
        full_name: str | None = None,
        account_type: AccountType | None = None,
        cooperative_id: UUID | None = None,
        profile_completed: bool | None = None,
    ) -> None: ...


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


class OTPRepository(ABC):
    @abstractmethod
    async def create_otp(self, *, phone_number: str, code: str, expires_at: datetime) -> None: ...

    @abstractmethod
    async def get_latest_unused_otp(self, phone_number: str) -> OTPCode | None: ...

    @abstractmethod
    async def mark_used(self, otp_id: UUID) -> None: ...

    @abstractmethod
    async def count_recent_requests(self, phone_number: str, since: datetime) -> int: ...


class CooperativeRepository(ABC):
    @abstractmethod
    async def get_by_id(self, cooperative_id: UUID) -> Cooperative | None: ...

    @abstractmethod
    async def create(self, *, name: str, created_by: UUID) -> Cooperative: ...


class DriverRepository(ABC):
    @abstractmethod
    async def get_manifest_stops(self, date: datetime, user_id: UUID, user_role: str) -> list[dict]: ...

    @abstractmethod
    async def get_shipment_by_id(self, shipment_id: UUID) -> dict | None: ...

    @abstractmethod
    async def confirm_stop(self, shipment_id: UUID, confirmed_at: datetime, lat: float, lon: float) -> dict: ...


class DeviceTokenRepository(ABC):
    @abstractmethod
    async def register(self, *, user_id: UUID, device_token: str, platform: str) -> None: ...

    @abstractmethod
    async def get_tokens_for_user(self, user_id: UUID) -> list[str]: ...


class ShipmentSyncStagingRepository(ABC):
    @abstractmethod
    async def get_by_client_id(self, client_id: str) -> ShipmentSyncStaging | None: ...

    @abstractmethod
    async def create(self, **kwargs) -> ShipmentSyncStaging: ...

    @abstractmethod
    async def update_photo_ref(self, client_id: str, photo_ref: str) -> None: ...

    @abstractmethod
    async def list_since(self, since: datetime, user_id: UUID | None = None, cooperative_id: UUID | None = None) -> list[ShipmentSyncStaging]: ...

    @abstractmethod
    async def list_pending_reconciliation(self, limit: int = 50) -> list[ShipmentSyncStaging]: ...

    @abstractmethod
    async def mark_reconciled(self, staging_id: UUID, shipment_id: UUID) -> None: ...

    @abstractmethod
    async def mark_failed(self, staging_id: UUID) -> None: ...
