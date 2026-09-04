from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_mobile_auth_service, get_otp_service
from app.application.mobile_auth_service import MobileAuthService
from app.application.mobile_schemas import (
    CompleteProfileRequest,
    MobileAuthTokensOut,
    MobileRefreshRequest,
    MobileUserOut,
    OTPRequest,
    OTPVerifyRequest,
)
from app.application.otp_service import OTPService
from app.domain.entities import User

router = APIRouter(prefix="/mobile/auth", tags=["mobile-auth"])


@router.post("/otp/request")
async def request_otp(
    payload: OTPRequest,
    otp_service: OTPService = Depends(get_otp_service),
):
    result = await otp_service.request_otp(payload.phone_number)
    return result


@router.post("/otp/verify")
async def verify_otp(
    payload: OTPVerifyRequest,
    otp_service: OTPService = Depends(get_otp_service),
    mobile_auth_service: MobileAuthService = Depends(get_mobile_auth_service),
):
    await otp_service.verify_otp(payload.phone_number, payload.code)
    user, access_token, expires_in, refresh_token = await mobile_auth_service.otp_login(payload.phone_number)
    tokens = MobileAuthTokensOut(
        access_token=access_token,
        expires_in=expires_in,
        refresh_token=refresh_token,
        user=MobileUserOut(
            id=user.id,
            phone_number=user.phone_number,
            role=user.role.value,
            full_name=user.full_name if user.profile_completed else None,
            account_type=user.account_type.value if user.account_type else None,
            cooperative_id=user.cooperative_id,
            profile_completed=user.profile_completed,
        ),
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
        user=MobileUserOut(
            id=user.id,
            phone_number=user.phone_number,
            role=user.role.value,
            full_name=user.full_name if user.profile_completed else None,
            account_type=user.account_type.value if user.account_type else None,
            cooperative_id=user.cooperative_id,
            profile_completed=user.profile_completed,
        ),
    )
    return {"data": tokens.model_dump(by_alias=True)}


@router.post("/complete-profile")
async def complete_profile(
    payload: CompleteProfileRequest,
    current_user: User = Depends(get_current_user),
    mobile_auth_service: MobileAuthService = Depends(get_mobile_auth_service),
):
    result = await mobile_auth_service.complete_profile(
        current_user.id,
        full_name=payload.full_name,
        account_type=payload.account_type,
        cooperative_name=payload.cooperative_name,
        cooperative_id=payload.cooperative_id,
    )
    user = result["user"]
    return {
        "data": {
            "user": MobileUserOut(
                id=user.id,
                phone_number=user.phone_number,
                role=user.role.value,
                full_name=user.full_name,
                account_type=user.account_type.value if user.account_type else None,
                cooperative_id=user.cooperative_id,
                profile_completed=user.profile_completed,
            ).model_dump(by_alias=True)
        }
    }
