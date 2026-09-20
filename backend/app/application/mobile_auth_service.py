from app.core.exceptions import NotFoundError, UnauthorizedError
from app.core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.domain.repositories import OTPRepository, UserRepository

_NO_ACCOUNT_MESSAGE = "No account found for this email. Ask your administrator or cooperative admin to add you first."


class MobileAuthService:
    def __init__(self, user_repository: UserRepository, otp_repository: OTPRepository):
        self._users = user_repository
        self._otp = otp_repository

    async def otp_login(self, email: str) -> tuple:
        # get_by_email is the same lookup web password-login uses — an
        # existing account (web or admin/cooperative-admin provisioned) can
        # OTP into the mobile app with just email access, no password
        # needed. Does NOT auto-create — every account is now provisioned
        # top-down by an administrator or cooperative admin; see
        # backend/docs/multitenancy_design.md.
        user = await self._users.get_by_email(email)
        if not user:
            raise NotFoundError(_NO_ACCOUNT_MESSAGE)
        return self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> tuple:
        try:
            user_id = decode_token(refresh_token, "refresh")
        except InvalidTokenError as exc:
            raise UnauthorizedError(str(exc)) from exc
        user = await self._users.get_by_id(user_id)
        if not user:
            raise UnauthorizedError("Session is no longer valid.")
        return self._issue_tokens(user)

    def _issue_tokens(self, user) -> tuple:
        access_token, expires_in = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return user, access_token, expires_in, refresh_token
