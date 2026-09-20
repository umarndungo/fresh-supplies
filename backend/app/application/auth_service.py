from uuid import UUID

from app.application.otp_service import OTPService
from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.domain.entities import User
from app.domain.repositories import UserRepository

_NO_ACCOUNT_MESSAGE = "No account found for this email. Ask your administrator to add you."


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self._users = user_repository

    async def request_login_otp(self, email: str, otp_service: OTPService) -> dict:
        # Unlike mobile's passwordless OTP login, this must NOT auto-create
        # an account on an unknown email — that would reopen the
        # self-registration hole this feature closes. See
        # backend/docs/multitenancy_design.md.
        user = await self._users.get_by_email(email)
        if not user:
            raise NotFoundError(_NO_ACCOUNT_MESSAGE)
        return await otp_service.request_otp(email)

    async def verify_login_otp(self, email: str, code: str, otp_service: OTPService) -> tuple[User, str, int, str]:
        user = await self._users.get_by_email(email)
        if not user:
            raise NotFoundError(_NO_ACCOUNT_MESSAGE)
        await otp_service.verify_otp(email, code)
        return self._issue_tokens(user)

    async def set_password(self, user_id: UUID, new_password: str) -> User:
        # Only for an account that hasn't set one yet (admin/cooperative-admin
        # provisioned, first login) — not a general change-password endpoint,
        # since it takes no proof of the current password.
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        if user.profile_completed:
            raise ConflictError("Password already set.")

        updated = await self._users.update_admin_user(
            user_id, hashed_password=hash_password(new_password), profile_completed=True
        )
        return updated

    async def login(self, *, email: str, password: str) -> tuple[User, str, int, str]:
        user = await self._users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedError("Your account has been deactivated.")
        return self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> tuple[User, str, int, str]:
        try:
            user_id = decode_token(refresh_token, "refresh")
        except InvalidTokenError as exc:
            raise UnauthorizedError(str(exc)) from exc

        user = await self._users.get_by_id(user_id)
        if not user:
            raise UnauthorizedError("Session is no longer valid.")
        return self._issue_tokens(user)

    async def get_current_user(self, access_token: str) -> User:
        try:
            user_id = decode_token(access_token, "access")
        except InvalidTokenError as exc:
            raise UnauthorizedError(str(exc)) from exc

        user = await self._users.get_by_id(user_id)
        if not user:
            raise UnauthorizedError("User no longer exists.")
        if not user.is_active:
            raise UnauthorizedError("Your account has been deactivated.")
        return user

    def _issue_tokens(self, user: User) -> tuple[User, str, int, str]:
        access_token, expires_in = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return user, access_token, expires_in, refresh_token
