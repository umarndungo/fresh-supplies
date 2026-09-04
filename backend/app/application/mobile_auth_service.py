from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.domain.entities import AccountType, UserRole
from app.domain.repositories import CooperativeRepository, OTPRepository, UserRepository


class MobileAuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        otp_repository: OTPRepository,
        cooperative_repository: CooperativeRepository,
    ):
        self._users = user_repository
        self._otp = otp_repository
        self._cooperatives = cooperative_repository

    async def otp_login(self, phone_number: str) -> tuple:
        user = await self._users.get_by_phone_number(phone_number)
        if not user:
            user = await self._users.create_phone_user(phone_number=phone_number)
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

    async def complete_profile(
        self,
        user_id: UUID,
        *,
        full_name: str,
        account_type: str,
        cooperative_name: str | None = None,
        cooperative_id: UUID | None = None,
    ) -> dict:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        if user.profile_completed:
            raise ConflictError("Profile already completed.")

        coop_id = None
        if account_type == "COOPERATIVE":
            if cooperative_id:
                coop = await self._cooperatives.get_by_id(cooperative_id)
                if not coop:
                    raise NotFoundError("Cooperative not found.")
                coop_id = coop.id
            elif cooperative_name:
                coop = await self._cooperatives.create(name=cooperative_name, created_by=user_id)
                coop_id = coop.id
            else:
                raise ConflictError("Either cooperative_name or cooperative_id is required for COOPERATIVE account type.")

        await self._users.update_profile(
            user_id,
            full_name=full_name,
            account_type=AccountType(account_type),
            cooperative_id=coop_id,
            profile_completed=True,
        )
        updated_user = await self._users.get_by_id(user_id)
        return {"user": updated_user}

    def _issue_tokens(self, user) -> tuple:
        access_token, expires_in = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return user, access_token, expires_in, refresh_token
