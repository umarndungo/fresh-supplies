import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Numeric
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities import CommodityClass, ProduceStatus, ShipmentStatus, UserRole
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
