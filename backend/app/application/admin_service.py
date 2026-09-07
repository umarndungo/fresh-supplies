from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.domain.entities import User, UserRole
from app.domain.repositories import UserRepository


class AdminService:
    """User administration operations (invite, roles, activation)."""

    def __init__(self, user_repository: UserRepository):
        self._users = user_repository

    async def list_users(self) -> list[User]:
        return await self._users.list_all()

    async def create_user(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
        role: UserRole,
        organization_name: str | None,
    ) -> User:
        existing = await self._users.get_by_email(email)
        if existing:
            raise ConflictError("An account with this email already exists.", field="email")

        return await self._users.create(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=role,
            organization_name=organization_name,
        )

    async def update_user(
        self,
        user_id: UUID,
        *,
        full_name: str | None = None,
        organization_name: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
        reset_password: str | None = None,
    ) -> User:
        user = await self._users.update_admin_user(
            user_id,
            full_name=full_name,
            organization_name=organization_name,
            role=role,
            is_active=is_active,
            hashed_password=hash_password(reset_password) if reset_password else None,
        )
        if user is None:
            raise NotFoundError("User not found.")
        return user

    async def delete_user(self, user_id: UUID, actor_id: UUID) -> None:
        if user_id == actor_id:
            raise ConflictError("You cannot delete your own account.")

        user = await self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")

        try:
            if not await self._users.delete(user_id):
                raise NotFoundError("User not found.")
        except IntegrityError as exc:
            raise ConflictError(
                "This user has existing records and cannot be deleted. "
                "Deactivate the account instead."
            ) from exc