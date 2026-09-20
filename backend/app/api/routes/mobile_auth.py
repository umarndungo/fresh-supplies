from fastapi import APIRouter, Depends

from app.api.deps import get_mobile_auth_service, get_otp_service
from app.application.mobile_auth_service import MobileAuthService
from app.application.mobile_schemas import (
    MobileAuthTokensOut,
    MobileRefreshRequest,
    MobileUserOut,
    OTPRequest,
    OTPVerifyRequest,
)
from app.application.otp_service import OTPService
from app.domain.entities import User

router = APIRouter(prefix="/mobile/auth", tags=["mobile-auth"])


def _to_mobile_user_out(user: User) -> MobileUserOut:
    return MobileUserOut(
        id=user.id,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role.value,
        full_name=user.full_name,
        account_type=user.account_type.value if user.account_type else None,
        cooperative_id=user.cooperative_id,
        profile_completed=user.profile_completed,
    )


@router.post("/otp/request")
async def request_otp(
    payload: OTPRequest,
    otp_service: OTPService = Depends(get_otp_service),
):
    result = await otp_service.request_otp(payload.email)
    return result


@router.post("/otp/verify")
async def verify_otp(
    payload: OTPVerifyRequest,
    otp_service: OTPService = Depends(get_otp_service),
    mobile_auth_service: MobileAuthService = Depends(get_mobile_auth_service),
):
    await otp_service.verify_otp(payload.email, payload.code)
    user, access_token, expires_in, refresh_token = await mobile_auth_service.otp_login(payload.email)
    tokens = MobileAuthTokensOut(
        access_token=access_token,
        expires_in=expires_in,
        refresh_token=refresh_token,
        user=_to_mobile_user_out(user),
    )
    return {"data": tokens.model_dump(by_alias=True)}


@router.post("/refresh")
async def refresh(
    payload: MobileRefreshRequest,
    mobile_auth_service: MobileAuthService = Depends(get_mobile_auth_service),
):
    user, access_token, expires_in, refresh_token = await mobile_auth_service.refresh(payload.refresh_token)
    tokens = MobileAuthTokensOut(
        access_token=access_token,
        expires_in=expires_in,
        refresh_token=refresh_token,
        user=_to_mobile_user_out(user),
    )
    return {"data": tokens.model_dump(by_alias=True)}
