from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class UserRole(str, Enum):
    ADMINISTRATOR = "ADMINISTRATOR"
    LOGISTICS_MANAGER = "LOGISTICS_MANAGER"
    FARMER_COOPERATIVE = "FARMER_COOPERATIVE"
    MARKET_ANALYST = "MARKET_ANALYST"


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
