from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_device_service
from app.application.device_service import DeviceService
from app.application.mobile_schemas import DeviceRegisterRequest, DeviceRegisterResponse
from app.domain.entities import User

router = APIRouter(prefix="/mobile/devices", tags=["mobile-devices"])


@router.post("/register")
async def register_device(
    payload: DeviceRegisterRequest,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    result = await service.register_device(
        current_user.id, payload.device_token, payload.platform
    )
    return DeviceRegisterResponse(**result).model_dump(by_alias=True)
