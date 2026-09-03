from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.domain.entities import User, UserRole
from app.domain.repositories import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self._users = user_repository

    async def register(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
        role: UserRole,
        organization_name: str | None,
    ) -> tuple[User, str, int, str]:
        existing = await self._users.get_by_email(email)
        if existing:
            raise ConflictError("An account with this email already exists.", field="email")

        user = await self._users.create(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=role,
            organization_name=organization_name,
        )
        return self._issue_tokens(user)

    async def login(self, *, email: str, password: str) -> tuple[User, str, int, str]:
        user = await self._users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password.")
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
        return user

    def _issue_tokens(self, user: User) -> tuple[User, str, int, str]:
        access_token, expires_in = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return user, access_token, expires_in, refresh_token
