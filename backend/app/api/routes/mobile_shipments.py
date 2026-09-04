from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, Form, Query

from app.api.deps import get_current_user, get_mobile_shipment_service, get_mobile_recommendation_service
from app.application.mobile_recommendation_service import MobileRecommendationService
from app.application.mobile_shipment_service import MobileShipmentService
from app.application.mobile_schemas import (
    ShipmentSyncRequest,
    ShipmentSyncResponse,
    ShipmentSyncResultItem,
    PhotoUploadResponse,
    SyncStatusItem,
    SyncStatusResponse,
    MobileRecommendationResponse,
)
from app.domain.entities import User

router = APIRouter(prefix="/mobile/shipments", tags=["mobile-shipments"])


@router.post("/sync")
async def sync_shipments(
    payload: ShipmentSyncRequest,
    current_user: User = Depends(get_current_user),
    service: MobileShipmentService = Depends(get_mobile_shipment_service),
):
    results = await service.sync_shipments(
        shipments=[item.model_dump() for item in payload.shipments],
        user=current_user,
    )
    return {
        "results": [
            ShipmentSyncResultItem(**r).model_dump(by_alias=True)
            for r in results
        ]
    }


@router.post("/photo-upload")
async def upload_photo(
    client_id: str = Form(...),
    file: UploadFile = File(...),
    _current_user: User = Depends(get_current_user),
    service: MobileShipmentService = Depends(get_mobile_shipment_service),
):
    result = await service.upload_photo(client_id=client_id, file=file)
    return PhotoUploadResponse(**result).model_dump(by_alias=True)


@router.get("/sync-status")
async def sync_status(
    since: datetime = Query(..., alias="since"),
    current_user: User = Depends(get_current_user),
    service: MobileShipmentService = Depends(get_mobile_shipment_service),
):
    changes = await service.get_sync_status(since=since, user=current_user)
    return {
        "changes": [
            SyncStatusItem(**c).model_dump(by_alias=True)
            for c in changes
        ]
    }


@router.get("/{shipment_id}/recommendation")
async def get_recommendation(
    shipment_id: UUID,
    crop: str = Query(...),
    quantity_kg: float = Query(..., alias="quantityKg"),
    lat: float = Query(...),
    lon: float = Query(...),
    accept_language: str = Query(default="en", alias="Accept-Language"),
    _current_user: User = Depends(get_current_user),
    service: MobileRecommendationService = Depends(get_mobile_recommendation_service),
):
    result = await service.get_recommendation(
        shipment_id=shipment_id,
        crop=crop,
        quantity_kg=quantity_kg,
        lat=lat,
        lon=lon,
        locale=accept_language,
    )
    return MobileRecommendationResponse(**result).model_dump(by_alias=True)
