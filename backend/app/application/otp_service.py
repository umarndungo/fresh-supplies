import random
import string
from datetime import datetime, timedelta, timezone

from fastapi.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.email_sender import send_otp_email
from app.core.exceptions import UnauthorizedError
from app.domain.repositories import OTPRepository


class OTPService:
    def __init__(self, otp_repository: OTPRepository):
        self._otp = otp_repository

    async def request_otp(self, email: str) -> dict:
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=settings.OTP_RATE_LIMIT_WINDOW_MINUTES)
        recent_count = await self._otp.count_recent_requests(email, since=window_start)
        if recent_count >= settings.OTP_RATE_LIMIT_PER_MINUTE:
            raise UnauthorizedError("Too many requests. Please try again later.")

        code = "".join(random.choices(string.digits, k=6))
        expires_at = now + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        await self._otp.create_otp(identifier=email, code=code, expires_at=expires_at)
        # smtplib is blocking; keep it off the event loop. Never let a
        # delivery failure surface as a 500 — see send_otp_email's own
        # "fail open, log loud" note.
        await run_in_threadpool(send_otp_email, email, code, settings.OTP_EXPIRE_MINUTES)
        return {"status": "sent", "expires_in_seconds": settings.OTP_EXPIRE_MINUTES * 60}

    async def verify_otp(self, email: str, code: str) -> bool:
        otp = await self._otp.get_latest_unused_otp(email)
        if not otp:
            raise UnauthorizedError("No valid OTP found. Please request a new one.")
        if datetime.now(timezone.utc) > otp.expires_at:
            raise UnauthorizedError("OTP has expired. Please request a new one.")
        if otp.code != code:
            raise UnauthorizedError("Invalid OTP code.")
        await self._otp.mark_used(otp.id)
        return True
