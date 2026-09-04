import random
import string
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.domain.repositories import OTPRepository


class OTPService:
    def __init__(self, otp_repository: OTPRepository):
        self._otp = otp_repository

    async def request_otp(self, phone_number: str) -> dict:
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=settings.OTP_RATE_LIMIT_WINDOW_MINUTES)
        recent_count = await self._otp.count_recent_requests(phone_number, since=window_start)
        if recent_count >= settings.OTP_RATE_LIMIT_PER_MINUTE:
            raise UnauthorizedError("Too many requests. Please try again later.")

        code = "".join(random.choices(string.digits, k=6))
        expires_at = now + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        await self._otp.create_otp(phone_number=phone_number, code=code, expires_at=expires_at)
        return {"status": "sent", "expires_in_seconds": settings.OTP_EXPIRE_MINUTES * 60}

    async def verify_otp(self, phone_number: str, code: str) -> bool:
        otp = await self._otp.get_latest_unused_otp(phone_number)
        if not otp:
            raise UnauthorizedError("No valid OTP found. Please request a new one.")
        if datetime.now(timezone.utc) > otp.expires_at:
            raise UnauthorizedError("OTP has expired. Please request a new one.")
        if otp.code != code:
            raise UnauthorizedError("Invalid OTP code.")
        await self._otp.mark_used(otp.id)
        return True
