from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class UserRole(str, Enum):
    ADMINISTRATOR = "ADMINISTRATOR"
    LOGISTICS_MANAGER = "LOGISTICS_MANAGER"
    FARMER_COOPERATIVE = "FARMER_COOPERATIVE"
    MARKET_ANALYST = "MARKET_ANALYST"


class AccountType(str, Enum):
    COOPERATIVE = "COOPERATIVE"
    INDIVIDUAL = "INDIVIDUAL"


class ReconciliationStatus(str, Enum):
    PENDING = "PENDING"
    RECONCILED = "RECONCILED"
    FAILED = "FAILED"


class OwnerType(str, Enum):
    COOPERATIVE = "COOPERATIVE"
    INDIVIDUAL = "INDIVIDUAL"


@dataclass(frozen=True, slots=True)
class User:
    id: UUID
    email: str
    full_name: str
    hashed_password: str
    role: UserRole
    organization_name: str | None
    avatar_url: str | None
    created_at: datetime
    phone_number: str | None
    account_type: AccountType | None
    cooperative_id: UUID | None
    phone_verified: bool
    profile_completed: bool


class ShipmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class ProduceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SHIPPED = "SHIPPED"
    SPOILED = "SPOILED"


class CommodityClass(str, Enum):
    PERISHABLE = "PERISHABLE"
    STAPLE = "STAPLE"


@dataclass(frozen=True, slots=True)
class Shipment:
    id: UUID
    origin: str
    destination: str
    produce_type: str
    status: ShipmentStatus
    scheduled_date: datetime
    delivery_date: datetime | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class ProduceItem:
    id: UUID
    name: str
    variety: str
    quantity_kg: float
    unit_price: float
    quality_grade: str
    harvest_date: datetime
    storage_location: str
    commodity_class: CommodityClass
    cooperative_id: UUID
    status: ProduceStatus
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class OTPCode:
    id: UUID
    phone_number: str
    code: str
    expires_at: datetime
    used: bool
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Cooperative:
    id: UUID
    name: str
    created_by: UUID
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ShipmentSyncStaging:
    id: UUID
    client_id: str
    crop: str
    quantity_kg: float
    captured_at: datetime
    location_lat: float
    location_lon: float
    photo_ref: str | None
    photo_status: str | None
    notes: str | None
    owner_type: OwnerType
    cooperative_id: UUID | None
    submitted_by_user_id: UUID
    sync_received_at: datetime
    reconciliation_status: ReconciliationStatus
    reconciled_shipment_id: UUID | None


@dataclass(frozen=True, slots=True)
class DeviceToken:
    id: UUID
    user_id: UUID
    device_token: str
    platform: str
    created_at: datetime
