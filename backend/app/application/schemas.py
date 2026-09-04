from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.domain.entities import CommodityClass, ProduceStatus, ShipmentStatus, UserRole


class UserOut(BaseModel):
    id: UUID
    email: EmailStr | None = None
    full_name: str = Field(serialization_alias="fullName")
    role: UserRole
    organization_name: str | None = Field(serialization_alias="organizationName")
    avatar_url: str | None = Field(serialization_alias="avatarUrl")
    phone_number: str | None = Field(serialization_alias="phoneNumber")
    account_type: str | None = Field(serialization_alias="accountType")
    cooperative_id: UUID | None = Field(serialization_alias="cooperativeId")
    phone_verified: bool = Field(serialization_alias="phoneVerified")
    profile_completed: bool = Field(serialization_alias="profileCompleted")
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class AuthTokensOut(BaseModel):
    access_token: str = Field(serialization_alias="accessToken")
    expires_in: int = Field(serialization_alias="expiresIn")
    user: UserOut

    model_config = {"populate_by_name": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class RegisterRequest(BaseModel):
    full_name: str = Field(alias="fullName", min_length=2)
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole
    organization_name: str | None = Field(default=None, alias="organizationName")

    model_config = {"populate_by_name": True}

    @field_validator("password")
    @classmethod
    def password_complexity(cls, value: str) -> str:
        if not any(c.isupper() for c in value):
            raise ValueError("Include at least one uppercase letter")
        if not any(c.islower() for c in value):
            raise ValueError("Include at least one lowercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Include at least one number")
        return value


class ShipmentOut(BaseModel):
    id: UUID
    origin: str
    destination: str
    produce_type: str = Field(serialization_alias="produceType")
    status: ShipmentStatus
    scheduled_date: datetime = Field(serialization_alias="scheduledDate")
    delivery_date: datetime | None = Field(serialization_alias="deliveryDate")
    created_by: UUID = Field(serialization_alias="createdBy")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class CreateShipmentRequest(BaseModel):
    origin: str = Field(min_length=2)
    destination: str = Field(min_length=2)
    produce_type: str = Field(alias="produceType", min_length=2)
    scheduled_date: datetime = Field(alias="scheduledDate")

    model_config = {"populate_by_name": True}


class UpdateShipmentRequest(BaseModel):
    status: ShipmentStatus | None = None
    delivery_date: datetime | None = Field(default=None, alias="deliveryDate")

    model_config = {"populate_by_name": True}


class ProduceOut(BaseModel):
    id: UUID
    name: str
    variety: str
    quantity_kg: float = Field(serialization_alias="quantityKg")
    unit_price: float = Field(serialization_alias="unitPrice")
    quality_grade: str = Field(serialization_alias="qualityGrade")
    harvest_date: datetime = Field(serialization_alias="harvestDate")
    storage_location: str = Field(serialization_alias="storageLocation")
    commodity_class: CommodityClass = Field(serialization_alias="commodityClass")
    cooperative_id: UUID = Field(serialization_alias="cooperativeId")
    status: ProduceStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class CreateProduceRequest(BaseModel):
    name: str = Field(min_length=2)
    variety: str = Field(min_length=2)
    quantity_kg: float = Field(alias="quantityKg", gt=0)
    unit_price: float = Field(alias="unitPrice", gt=0)
    quality_grade: str = Field(alias="qualityGrade", min_length=1)
    harvest_date: datetime = Field(alias="harvestDate")
    storage_location: str = Field(alias="storageLocation", min_length=2)
    commodity_class: CommodityClass = Field(default=CommodityClass.PERISHABLE, alias="commodityClass")

    model_config = {"populate_by_name": True}


class UpdateProduceRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    variety: str | None = Field(default=None, min_length=2)
    quantity_kg: float | None = Field(default=None, alias="quantityKg", gt=0)
    unit_price: float | None = Field(default=None, alias="unitPrice", gt=0)
    quality_grade: str | None = Field(default=None, alias="qualityGrade", min_length=1)
    harvest_date: datetime | None = Field(default=None, alias="harvestDate")
    storage_location: str | None = Field(default=None, alias="storageLocation", min_length=2)
    commodity_class: CommodityClass | None = Field(default=None, alias="commodityClass")
    status: ProduceStatus | None = None

    model_config = {"populate_by_name": True}
