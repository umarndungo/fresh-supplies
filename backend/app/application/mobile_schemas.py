from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class OTPRequest(BaseModel):
    phone_number: str = Field(alias="phoneNumber")

    model_config = {"populate_by_name": True}


class OTPVerifyRequest(BaseModel):
    phone_number: str = Field(alias="phoneNumber")
    code: str = Field(min_length=6, max_length=6)

    model_config = {"populate_by_name": True}


class MobileAuthTokensOut(BaseModel):
    access_token: str = Field(serialization_alias="accessToken")
    expires_in: int = Field(serialization_alias="expiresIn")
    refresh_token: str = Field(serialization_alias="refreshToken")
    user: "MobileUserOut"

    model_config = {"populate_by_name": True}


class MobileUserOut(BaseModel):
    id: UUID
    phone_number: str | None = Field(serialization_alias="phoneNumber")
    role: str
    full_name: str | None = Field(serialization_alias="fullName")
    account_type: str | None = Field(serialization_alias="accountType")
    cooperative_id: UUID | None = Field(serialization_alias="cooperativeId")
    profile_completed: bool = Field(serialization_alias="profileCompleted")

    model_config = {"populate_by_name": True, "from_attributes": True}


class MobileRefreshRequest(BaseModel):
    refresh_token: str = Field(alias="refreshToken")

    model_config = {"populate_by_name": True}


class CompleteProfileRequest(BaseModel):
    full_name: str = Field(alias="fullName", min_length=2)
    account_type: str = Field(alias="accountType")
    cooperative_name: str | None = Field(default=None, alias="cooperativeName")
    cooperative_id: UUID | None = Field(default=None, alias="cooperativeId")

    model_config = {"populate_by_name": True}


class LocationPayload(BaseModel):
    lat: float
    lon: float


class ShipmentSyncItem(BaseModel):
    client_id: str = Field(alias="clientId")
    crop: str
    quantity_kg: float = Field(alias="quantityKg")
    captured_at: datetime = Field(alias="capturedAt")
    location: LocationPayload
    photo_ref: str | None = Field(default=None, alias="photoRef")
    notes: str | None = None

    model_config = {"populate_by_name": True}


class ShipmentSyncRequest(BaseModel):
    shipments: list[ShipmentSyncItem]


class ShipmentSyncResultItem(BaseModel):
    client_id: str = Field(serialization_alias="clientId")
    status: str
    server_id: UUID | None = Field(default=None, serialization_alias="serverId")
    risk_tier: str | None = Field(default=None, serialization_alias="riskTier")
    error: str | None = None

    model_config = {"populate_by_name": True}


class ShipmentSyncResponse(BaseModel):
    results: list[ShipmentSyncResultItem]


class PhotoUploadResponse(BaseModel):
    photo_ref: str = Field(serialization_alias="photoRef")
    status: str

    model_config = {"populate_by_name": True}


class SyncStatusItem(BaseModel):
    client_id: str = Field(serialization_alias="clientId")
    server_id: UUID = Field(serialization_alias="serverId")
    status: str
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = {"populate_by_name": True}


class SyncStatusResponse(BaseModel):
    changes: list[SyncStatusItem]


class DriverManifestStop(BaseModel):
    shipment_id: UUID = Field(serialization_alias="shipmentId")
    owner_type: str = Field(serialization_alias="ownerType")
    cooperative_name: str | None = Field(default=None, serialization_alias="cooperativeName")
    crop: str
    quantity_kg: float = Field(serialization_alias="quantityKg")
    pickup_location: dict
    destination_market: str = Field(serialization_alias="destinationMarket")
    risk_tier: str = Field(serialization_alias="riskTier")
    sequence: int

    model_config = {"populate_by_name": True}


class DriverManifestResponse(BaseModel):
    stops: list[DriverManifestStop]


class StopConfirmRequest(BaseModel):
    confirmed_at: datetime = Field(alias="confirmedAt")
    location: LocationPayload

    model_config = {"populate_by_name": True}


class StopConfirmResponse(BaseModel):
    status: str
    shipment_status: str = Field(serialization_alias="shipmentStatus")

    model_config = {"populate_by_name": True}


class DeviceRegisterRequest(BaseModel):
    device_token: str = Field(alias="deviceToken")
    platform: str

    model_config = {"populate_by_name": True}


class DeviceRegisterResponse(BaseModel):
    status: str

    model_config = {"populate_by_name": True}


class MobileRecommendationResponse(BaseModel):
    risk_tier: str = Field(serialization_alias="riskTier")
    risk_label: str = Field(serialization_alias="riskLabel")
    recommended_market: dict | None = Field(default=None, serialization_alias="recommendedMarket")
    alternate_markets: list[dict] = Field(default_factory=list, serialization_alias="alternateMarkets")

    model_config = {"populate_by_name": True}
