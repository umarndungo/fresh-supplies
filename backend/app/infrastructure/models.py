import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities import (
    AccountType,
    CommodityClass,
    OwnerType,
    ProduceStatus,
    ReconciliationStatus,
    ShipmentStatus,
    UserRole,
)
from app.infrastructure.db import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name="user_role"), nullable=False)
    organization_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    account_type: Mapped[AccountType | None] = mapped_column(
        SAEnum(AccountType, name="account_type_enum", create_type=False), nullable=True
    )
    cooperative_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("cooperatives.id"), nullable=True
    )
    phone_verified: Mapped[bool] = mapped_column(default=False)
    profile_completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ShipmentModel(Base):
    __tablename__ = "shipments"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    origin: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    produce_type: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ShipmentStatus] = mapped_column(
        SAEnum(ShipmentStatus, name="shipment_status"), nullable=False, default=ShipmentStatus.SCHEDULED
    )
    scheduled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    delivery_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner_type: Mapped[OwnerType | None] = mapped_column(
        SAEnum(OwnerType, name="owner_type_enum", create_type=False), nullable=True
    )
    cooperative_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("cooperatives.id"), nullable=True
    )
    submitted_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    photo_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    photo_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    client_id: Mapped[str | None] = mapped_column(String(36), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ProduceModel(Base):
    __tablename__ = "produce"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    variety: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quality_grade: Mapped[str] = mapped_column(String(50), nullable=False)
    harvest_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    storage_location: Mapped[str] = mapped_column(String(255), nullable=False)
    commodity_class: Mapped[CommodityClass] = mapped_column(
        SAEnum(CommodityClass, name="commodity_class"), nullable=False, default=CommodityClass.PERISHABLE
    )
    cooperative_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[ProduceStatus] = mapped_column(
        SAEnum(ProduceStatus, name="produce_status"), nullable=False, default=ProduceStatus.AVAILABLE
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class CooperativeModel(Base):
    __tablename__ = "cooperatives"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OTPCodeModel(Base):
    __tablename__ = "otp_codes"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(6), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ShipmentSyncStagingModel(Base):
    __tablename__ = "shipment_sync_staging"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    crop: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location_lat: Mapped[float] = mapped_column(nullable=False)
    location_lon: Mapped[float] = mapped_column(nullable=False)
    photo_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    photo_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_type: Mapped[OwnerType] = mapped_column(
        SAEnum(OwnerType, name="owner_type_enum", create_type=False), nullable=False
    )
    cooperative_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("cooperatives.id"), nullable=True
    )
    submitted_by_user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    sync_received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    reconciliation_status: Mapped[ReconciliationStatus] = mapped_column(
        SAEnum(ReconciliationStatus, name="reconciliation_status_enum", create_type=False),
        nullable=False,
        default=ReconciliationStatus.PENDING,
    )
    reconciled_shipment_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("shipments.id"), nullable=True
    )


class DeviceTokenModel(Base):
    __tablename__ = "device_tokens"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    device_token: Mapped[str] = mapped_column(String(512), nullable=False)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
