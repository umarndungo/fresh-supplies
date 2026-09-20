from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable
from uuid import UUID

from app.domain.entities import (
    Cooperative,
    CooperativeAccessGrant,
    CooperativeRole,
    OTPCode,
    OwnerType,
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
    async def create_pending(
        self,
        *,
        email: str,
        full_name: str,
        role: UserRole,
        organization_name: str | None = None,
        cooperative_id: UUID | None = None,
        cooperative_role: CooperativeRole | None = None,
    ) -> User:
        """Creates a passwordless, profile_completed=False account for
        top-down provisioning (an ADMINISTRATOR or cooperative admin invites
        someone). The invitee's first login is an emailed OTP, after which
        they set their own password (AuthService.set_password)."""
        ...

    @abstractmethod
    async def list_all(self) -> list[User]: ...

    @abstractmethod
    async def list_by_cooperative(self, cooperative_id: UUID) -> list[User]: ...

    @abstractmethod
    async def update_admin_user(
        self,
        user_id: UUID,
        *,
        full_name: str | None = None,
        organization_name: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
        hashed_password: str | None = None,
        cooperative_id: UUID | None = None,
        cooperative_role: CooperativeRole | None = None,
        profile_completed: bool | None = None,
    ) -> User | None: ...

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool: ...


class ShipmentRepository(ABC):
    @abstractmethod
    async def list_all(
        self,
        *,
        owner_id: UUID | None = None,
        cooperative_ids: Iterable[UUID] | None = None,
        driver_user_id: UUID | None = None,
    ) -> list[Shipment]: ...

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
        owner_type: OwnerType = OwnerType.INDIVIDUAL,
        cooperative_id: UUID | None = None,
        produce_id: UUID | None = None,
        harvest_date_snapshot: datetime | None = None,
        storage_spoilage_probability_snapshot: float | None = None,
        estimated_shelf_life_days_snapshot: float | None = None,
        storage_temperature_c_snapshot: float | None = None,
        storage_pressure_psi_snapshot: float | None = None,
    ) -> Shipment: ...

    @abstractmethod
    async def update(
        self,
        shipment_id: UUID,
        *,
        status: ShipmentStatus | None = None,
        delivery_date: datetime | None = None,
        spoilage_probability: float | None = None,
        risk_tier: str | None = None,
        spoil_prediction: bool | None = None,
        market_recommendations: list[dict] | None = None,
        produce_id: UUID | None = None,
        harvest_date_snapshot: datetime | None = None,
        storage_spoilage_probability_snapshot: float | None = None,
        estimated_shelf_life_days_snapshot: float | None = None,
        storage_temperature_c_snapshot: float | None = None,
        storage_pressure_psi_snapshot: float | None = None,
        driver_user_id: UUID | None = None,
    ) -> Shipment | None: ...

    @abstractmethod
    async def delete(self, shipment_id: UUID) -> bool: ...


class ProduceRepository(ABC):
    @abstractmethod
    async def list_all(
        self, *, owner_id: UUID | None = None, cooperative_ids: Iterable[UUID] | None = None
    ) -> list[ProduceItem]: ...

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
        created_by: UUID,
        owner_type: OwnerType,
        status: ProduceStatus,
        cooperative_id: UUID | None = None,
        storage_temperature_c: float | None = None,
        storage_pressure_psi: float | None = None,
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
        storage_temperature_c: float | None = None,
        storage_pressure_psi: float | None = None,
        storage_spoilage_probability: float | None = None,
        storage_risk_tier: str | None = None,
        storage_spoil_prediction: bool | None = None,
        estimated_shelf_life_days: float | None = None,
    ) -> ProduceItem | None: ...

    @abstractmethod
    async def delete(self, produce_id: UUID) -> bool: ...


class OTPRepository(ABC):
    """`identifier` is an email address — mobile login OTP switched from
    phone number to email; see 20260918_otp_email_identifier."""

    @abstractmethod
    async def create_otp(self, *, identifier: str, code: str, expires_at: datetime) -> None: ...

    @abstractmethod
    async def get_latest_unused_otp(self, identifier: str) -> OTPCode | None: ...

    @abstractmethod
    async def mark_used(self, otp_id: UUID) -> None: ...

    @abstractmethod
    async def count_recent_requests(self, identifier: str, since: datetime) -> int: ...


class CooperativeRepository(ABC):
    @abstractmethod
    async def get_by_id(self, cooperative_id: UUID) -> Cooperative | None: ...

    @abstractmethod
    async def create(self, *, name: str, created_by: UUID) -> Cooperative: ...

    @abstractmethod
    async def list_all(self) -> list[Cooperative]: ...

    @abstractmethod
    async def update(self, cooperative_id: UUID, *, name: str | None = None) -> Cooperative | None: ...


class CooperativeAccessGrantRepository(ABC):
    """See backend/docs/multitenancy_design.md §2.4/§7.3. `create()` must
    reject a grant whose target user is not LOGISTICS_MANAGER or
    MARKET_ANALYST — ADMINISTRATOR is never a valid grantee, enforced in
    CooperativeAccessGrantService rather than here (the service already
    loads the target user to authorize the caller and give a clean error)."""

    @abstractmethod
    async def list_cooperative_ids_for(self, user_id: UUID) -> list[UUID]: ...

    @abstractmethod
    async def create(self, *, user_id: UUID, cooperative_id: UUID, granted_by: UUID) -> CooperativeAccessGrant: ...

    @abstractmethod
    async def delete(self, grant_id: UUID) -> bool: ...

    @abstractmethod
    async def list_for_cooperative(self, cooperative_id: UUID) -> list[CooperativeAccessGrant]: ...


class TenantUsageRepository(ABC):
    """Aggregate-only counts for ADMINISTRATOR billing/usage (§7.2 of the
    design doc). Every implementation must use COUNT/SUM SQL only — never
    select or return shipment/produce row content."""

    @abstractmethod
    async def get_cooperative_usage(self, cooperative_id: UUID) -> dict: ...

    @abstractmethod
    async def list_cooperative_usage(self) -> list[dict]: ...


class DriverRepository(ABC):
    @abstractmethod
    async def get_manifest_stops(
        self,
        date: datetime,
        *,
        owner_id: UUID | None = None,
        cooperative_ids: Iterable[UUID] | None = None,
        driver_user_id: UUID | None = None,
    ) -> list[dict]: ...

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
    async def rollback(self) -> None: ...

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
