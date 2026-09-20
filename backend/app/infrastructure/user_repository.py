from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import AccountType, CooperativeRole, User, UserRole
from app.domain.repositories import UserRepository
from app.infrastructure.models import UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        full_name=model.full_name,
        hashed_password=model.hashed_password,
        role=model.role,
        organization_name=model.organization_name,
        avatar_url=model.avatar_url,
        created_at=model.created_at,
        phone_number=model.phone_number,
        account_type=model.account_type,
        cooperative_id=model.cooperative_id,
        phone_verified=model.phone_verified,
        profile_completed=model.profile_completed,
        is_active=model.is_active,
        cooperative_role=model.cooperative_role,
    )


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return _to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create(
        self,
        *,
        email: str,
        full_name: str,
        hashed_password: str,
        role: UserRole,
        organization_name: str | None,
    ) -> User:
        model = UserModel(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=role,
            organization_name=organization_name,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get_by_phone_number(self, phone_number: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.phone_number == phone_number)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create_pending(
        self,
        *,
        email: str,
        full_name: str,
        role: UserRole,
        organization_name: str | None = None,
        cooperative_id: UUID | None = None,
        cooperative_role: CooperativeRole | None = None,
    ) -> User:
        # Top-down provisioning (admin/cooperative-admin invite): no password
        # yet — hashed_password is a sentinel, never checked by verify_password.
        # The invitee's first login is an emailed OTP, then they set a real
        # password (AuthService.set_password), which flips profile_completed.
        model = UserModel(
            email=email,
            full_name=full_name,
            hashed_password="pending_invite_no_password",
            role=role,
            organization_name=organization_name,
            account_type=AccountType.COOPERATIVE if cooperative_id else AccountType.INDIVIDUAL,
            cooperative_id=cooperative_id,
            cooperative_role=cooperative_role,
            phone_verified=False,
            profile_completed=False,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def list_all(self) -> list[User]:
        result = await self._session.execute(
            select(UserModel).order_by(UserModel.created_at.desc())
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def list_by_cooperative(self, cooperative_id: UUID) -> list[User]:
        result = await self._session.execute(
            select(UserModel)
            .where(UserModel.cooperative_id == cooperative_id)
            .order_by(UserModel.created_at.desc())
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def update_admin_user(
        self,
        user_id: UUID,
        *,
        full_name: str | None = None,
        organization_name: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
        hashed_password: str | None = None,
        cooperative_id: UUID | None = None,
        cooperative_role: CooperativeRole | None = None,
        profile_completed: bool | None = None,
    ) -> User | None:
        model = await self._session.get(UserModel, user_id)
        if model is None:
            return None
        if full_name is not None:
            model.full_name = full_name
        if organization_name is not None:
            model.organization_name = organization_name
        if role is not None:
            model.role = role
        if is_active is not None:
            model.is_active = is_active
        if hashed_password is not None:
            model.hashed_password = hashed_password
        if cooperative_id is not None:
            model.cooperative_id = cooperative_id
        if cooperative_role is not None:
            model.cooperative_role = cooperative_role
        if profile_completed is not None:
            model.profile_completed = profile_completed
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        model = await self._session.get(UserModel, user_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True
