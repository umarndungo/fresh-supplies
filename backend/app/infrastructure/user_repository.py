from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import AccountType, User, UserRole
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

    async def create_phone_user(self, *, phone_number: str) -> User:
        model = UserModel(
            email=f"pending_{phone_number}@phone.freshroute.local",
            full_name="",
            hashed_password="phone_no_password",
            role=UserRole.FARMER_COOPERATIVE,
            organization_name=None,
            phone_number=phone_number,
            phone_verified=True,
            profile_completed=False,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update_profile(
        self,
        user_id: UUID,
        *,
        full_name: str | None = None,
        account_type: AccountType | None = None,
        cooperative_id: UUID | None = None,
        profile_completed: bool | None = None,
    ) -> None:
        model = await self._session.get(UserModel, user_id)
        if model is None:
            return
        if full_name is not None:
            model.full_name = full_name
        if account_type is not None:
            model.account_type = account_type
        if cooperative_id is not None:
            model.cooperative_id = cooperative_id
        if profile_completed is not None:
            model.profile_completed = profile_completed
        await self._session.commit()
