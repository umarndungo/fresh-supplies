from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.domain.entities import CommodityClass, CooperativeRole, ProduceStatus, ShipmentStatus, UserRole


def _validate_password_complexity(value: str) -> str:
    if not any(c.isupper() for c in value):
        raise ValueError("Include at least one uppercase letter")
    if not any(c.islower() for c in value):
        raise ValueError("Include at least one lowercase letter")
    if not any(c.isdigit() for c in value):
        raise ValueError("Include at least one number")
    return value


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
    cooperative_role: CooperativeRole | None = Field(default=None, serialization_alias="cooperativeRole")
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


class OTPRequest(BaseModel):
    email: EmailStr

    model_config = {"populate_by_name": True}


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)

    model_config = {"populate_by_name": True}


class SetPasswordRequest(BaseModel):
    new_password: str = Field(alias="newPassword", min_length=8)

    model_config = {"populate_by_name": True}

    @field_validator("new_password")
    @classmethod
    def password_complexity(cls, value: str) -> str:
        return _validate_password_complexity(value)


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
    # Origin location (source)
    origin_latitude: float | None = Field(default=None, serialization_alias="originLatitude")
    origin_longitude: float | None = Field(default=None, serialization_alias="originLongitude")
    # Destination location (market)
    destination_latitude: float | None = Field(default=None, serialization_alias="destinationLatitude")
    destination_longitude: float | None = Field(default=None, serialization_alias="destinationLongitude")
    # ML prediction fields
    temperature_c: float | None = Field(default=None, serialization_alias="temperatureC")
    transit_duration_hr: float | None = Field(default=None, serialization_alias="transitDurationHr")
    pressure_psi: float | None = Field(default=None, serialization_alias="pressurePsi")
    baseline_loss_pct: float | None = Field(default=None, serialization_alias="baselineLossPct")
    quantity_kg: float | None = Field(default=None, serialization_alias="quantityKg")
    spoilage_probability: float | None = Field(default=None, serialization_alias="spoilageProbability")
    risk_tier: str | None = Field(default=None, serialization_alias="riskTier")
    spoil_prediction: bool | None = Field(default=None, serialization_alias="spoilPrediction")
    market_recommendations: list[dict] | None = Field(default=None, serialization_alias="marketRecommendations")
    produce_id: UUID | None = Field(default=None, serialization_alias="produceId")
    harvest_date_snapshot: datetime | None = Field(default=None, serialization_alias="harvestDateSnapshot")
    storage_spoilage_probability_snapshot: float | None = Field(default=None, serialization_alias="storageSpoilageProbabilitySnapshot")
    estimated_shelf_life_days_snapshot: float | None = Field(default=None, serialization_alias="estimatedShelfLifeDaysSnapshot")
    storage_temperature_c_snapshot: float | None = Field(default=None, serialization_alias="storageTemperatureCSnapshot")
    storage_pressure_psi_snapshot: float | None = Field(default=None, serialization_alias="storagePressurePsiSnapshot")
    driver_user_id: UUID | None = Field(default=None, serialization_alias="driverUserId")

    model_config = {"populate_by_name": True, "from_attributes": True}


class CreateShipmentRequest(BaseModel):
    origin: str = Field(min_length=2)
    destination: str = Field(min_length=2)
    produce_type: str = Field(alias="produceType", min_length=2)
    scheduled_date: datetime = Field(alias="scheduledDate")
    # Origin location (source) - for ML predictions
    origin_latitude: float | None = Field(default=None, alias="originLatitude", ge=-90, le=90)
    origin_longitude: float | None = Field(default=None, alias="originLongitude", ge=-180, le=180)
    # Destination location (market) coordinates - auto-filled from market selection
    destination_latitude: float | None = Field(default=None, alias="destinationLatitude", ge=-90, le=90)
    destination_longitude: float | None = Field(default=None, alias="destinationLongitude", ge=-180, le=180)
    # ML prediction fields (optional)
    temperature_c: float | None = Field(default=None, alias="temperatureC")
    transit_duration_hr: float | None = Field(default=None, alias="transitDurationHr")
    pressure_psi: float | None = Field(default=None, alias="pressurePsi")
    baseline_loss_pct: float | None = Field(default=None, alias="baselineLossPct")
    quantity_kg: float | None = Field(default=None, alias="quantityKg")
    produce_id: UUID | None = Field(default=None, alias="produceId")
    harvest_date_snapshot: datetime | None = Field(default=None, alias="harvestDateSnapshot")
    storage_spoilage_probability_snapshot: float | None = Field(default=None, alias="storageSpoilageProbabilitySnapshot", ge=0, le=1)
    estimated_shelf_life_days_snapshot: float | None = Field(default=None, alias="estimatedShelfLifeDaysSnapshot", ge=0)
    storage_temperature_c_snapshot: float | None = Field(default=None, alias="storageTemperatureCSnapshot", ge=-20, le=60)
    storage_pressure_psi_snapshot: float | None = Field(default=None, alias="storagePressurePsiSnapshot", ge=0)

    model_config = {"populate_by_name": True}


class AdminUserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str = Field(serialization_alias="fullName")
    role: UserRole
    organization_name: str | None = Field(serialization_alias="organizationName")
    avatar_url: str | None = Field(serialization_alias="avatarUrl")
    phone_number: str | None = Field(serialization_alias="phoneNumber")
    account_type: str | None = Field(serialization_alias="accountType")
    cooperative_id: UUID | None = Field(serialization_alias="cooperativeId")
    cooperative_role: str | None = Field(default=None, serialization_alias="cooperativeRole")
    phone_verified: bool = Field(serialization_alias="phoneVerified")
    profile_completed: bool = Field(serialization_alias="profileCompleted")
    is_active: bool = Field(serialization_alias="isActive")
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class AdminCreateUserRequest(BaseModel):
    """No password field: an admin-provisioned account is always created
    passwordless (profile_completed=False) and the invitee sets their own
    password on first login via emailed OTP — see
    backend/docs/multitenancy_design.md and AdminService.create_user."""

    full_name: str = Field(alias="fullName", min_length=2)
    email: EmailStr
    role: UserRole
    organization_name: str | None = Field(default=None, alias="organizationName")
    cooperative_id: UUID | None = Field(default=None, alias="cooperativeId")
    cooperative_role: CooperativeRole | None = Field(default=None, alias="cooperativeRole")

    model_config = {"populate_by_name": True}


class AdminUpdateUserRequest(BaseModel):
    full_name: str | None = Field(default=None, alias="fullName", min_length=2)
    organization_name: str | None = Field(default=None, alias="organizationName")
    role: UserRole | None = None
    is_active: bool | None = Field(default=None, alias="isActive")
    reset_password: str | None = Field(default=None, alias="resetPassword", min_length=8)
    cooperative_id: UUID | None = Field(default=None, alias="cooperativeId")
    cooperative_role: CooperativeRole | None = Field(default=None, alias="cooperativeRole")

    model_config = {"populate_by_name": True}

    @field_validator("reset_password")
    @classmethod
    def password_complexity(cls, value: str | None) -> str | None:
        return _validate_password_complexity(value) if value is not None else value


class CreateCooperativeMemberRequest(BaseModel):
    """Used by a cooperative admin (FARMER_COOPERATIVE + cooperative_role=ADMIN)
    to add a member or driver to their OWN cooperative. cooperative_id and
    cooperative_role are never taken from the client — CooperativeMemberService
    always derives them from the acting cooperative admin."""

    full_name: str = Field(alias="fullName", min_length=2)
    email: EmailStr
    role: UserRole

    model_config = {"populate_by_name": True}


class UpdateShipmentRequest(BaseModel):
    status: ShipmentStatus | None = None
    delivery_date: datetime | None = Field(default=None, alias="deliveryDate")
    spoilage_probability: float | None = Field(default=None, alias="spoilageProbability", ge=0, le=1)
    risk_tier: str | None = Field(default=None, alias="riskTier")
    spoil_prediction: bool | None = Field(default=None, alias="spoilPrediction")
    market_recommendations: list[dict] | None = Field(default=None, alias="marketRecommendations")
    produce_id: UUID | None = Field(default=None, alias="produceId")
    harvest_date_snapshot: datetime | None = Field(default=None, alias="harvestDateSnapshot")
    storage_spoilage_probability_snapshot: float | None = Field(default=None, alias="storageSpoilageProbabilitySnapshot", ge=0, le=1)
    estimated_shelf_life_days_snapshot: float | None = Field(default=None, alias="estimatedShelfLifeDaysSnapshot", ge=0)
    storage_temperature_c_snapshot: float | None = Field(default=None, alias="storageTemperatureCSnapshot", ge=-20, le=60)
    storage_pressure_psi_snapshot: float | None = Field(default=None, alias="storagePressurePsiSnapshot", ge=0)

    model_config = {"populate_by_name": True}


class AssignDriverRequest(BaseModel):
    driver_user_id: UUID = Field(alias="driverUserId")

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
    owner_type: str = Field(serialization_alias="ownerType")
    created_by: UUID = Field(serialization_alias="createdBy")
    # Null for an INDIVIDUAL/solo-owned item — see
    # backend/docs/multitenancy_design.md §2.1 (this used to be a mislabeled
    # required FK to the creator; it's now a real, optional cooperative FK).
    cooperative_id: UUID | None = Field(default=None, serialization_alias="cooperativeId")
    status: ProduceStatus
    storage_temperature_c: float | None = Field(default=None, serialization_alias="storageTemperatureC")
    storage_pressure_psi: float | None = Field(default=None, serialization_alias="storagePressurePsi")
    storage_spoilage_probability: float | None = Field(default=None, serialization_alias="storageSpoilageProbability")
    storage_risk_tier: str | None = Field(default=None, serialization_alias="storageRiskTier")
    storage_spoil_prediction: bool | None = Field(default=None, serialization_alias="storageSpoilPrediction")
    estimated_shelf_life_days: float | None = Field(default=None, serialization_alias="estimatedShelfLifeDays")
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
    storage_temperature_c: float | None = Field(default=None, alias="storageTemperatureC", ge=-20, le=60)
    storage_pressure_psi: float | None = Field(default=None, alias="storagePressurePsi", ge=0)

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
    storage_temperature_c: float | None = Field(default=None, alias="storageTemperatureC", ge=-20, le=60)
    storage_pressure_psi: float | None = Field(default=None, alias="storagePressurePsi", ge=0)
    storage_spoilage_probability: float | None = Field(default=None, alias="storageSpoilageProbability", ge=0, le=1)
    storage_risk_tier: str | None = Field(default=None, alias="storageRiskTier")
    storage_spoil_prediction: bool | None = Field(default=None, alias="storageSpoilPrediction")
    estimated_shelf_life_days: float | None = Field(default=None, alias="estimatedShelfLifeDays", ge=0)

    model_config = {"populate_by_name": True}


# --- Admin tenant lifecycle + billing usage (ADMINISTRATOR only) ---
# See backend/docs/multitenancy_design.md §7. TenantUsageOut is deliberately
# aggregate-only fields — never a shipment/produce row.


class TenantOut(BaseModel):
    id: UUID
    name: str
    created_by: UUID = Field(serialization_alias="createdBy")
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}


class CreateTenantRequest(BaseModel):
    name: str = Field(min_length=2)
    # Optional: provision the cooperative's initial admin in the same call.
    # Both-or-neither — see the model_validator below.
    admin_email: EmailStr | None = Field(default=None, alias="adminEmail")
    admin_full_name: str | None = Field(default=None, alias="adminFullName", min_length=2)

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def admin_fields_both_or_neither(self) -> "CreateTenantRequest":
        if (self.admin_email is None) != (self.admin_full_name is None):
            raise ValueError("adminEmail and adminFullName must be provided together.")
        return self


class UpdateTenantRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2)

    model_config = {"populate_by_name": True}


class TenantUsageOut(BaseModel):
    cooperative_id: UUID = Field(serialization_alias="cooperativeId")
    member_count: int = Field(serialization_alias="memberCount")
    shipment_count: int = Field(serialization_alias="shipmentCount")
    produce_item_count: int = Field(serialization_alias="produceItemCount")
    total_quantity_kg: float = Field(serialization_alias="totalQuantityKg")

    model_config = {"populate_by_name": True}


# --- Cooperative access grants (ADMINISTRATOR only) ---
# See backend/docs/multitenancy_design.md §2.4/§7.3.


class CreateGrantRequest(BaseModel):
    user_id: UUID = Field(alias="userId")
    cooperative_id: UUID = Field(alias="cooperativeId")

    model_config = {"populate_by_name": True}


class GrantOut(BaseModel):
    id: UUID
    user_id: UUID = Field(serialization_alias="userId")
    cooperative_id: UUID = Field(serialization_alias="cooperativeId")
    granted_by: UUID = Field(serialization_alias="grantedBy")
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}
