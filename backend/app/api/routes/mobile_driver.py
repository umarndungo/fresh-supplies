from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_driver_service
from app.application.driver_service import DriverService
from app.application.mobile_schemas import (
    DriverManifestResponse,
    DriverManifestStop,
    StopConfirmRequest,
    StopConfirmResponse,
)
from app.domain.entities import User

router = APIRouter(prefix="/mobile/driver", tags=["mobile-driver"])


@router.get("/manifest")
async def get_manifest(
    date: datetime = Query(..., alias="date"),
    current_user: User = Depends(get_current_user),
    service: DriverService = Depends(get_driver_service),
):
    stops = await service.get_manifest(date, current_user.id, current_user.role.value)
    return DriverManifestResponse(
        stops=[DriverManifestStop(**s) for s in stops]
    ).model_dump(by_alias=True)


@router.post("/stops/{shipment_id}/confirm")
async def confirm_stop(
    shipment_id: str,
    payload: StopConfirmRequest,
    _current_user: User = Depends(get_current_user),
    service: DriverService = Depends(get_driver_service),
):
    result = await service.confirm_stop(
        UUID(shipment_id),
        payload.confirmed_at,
        payload.location.lat,
        payload.location.lon,
    )
    return StopConfirmResponse(**result).model_dump(by_alias=True)
