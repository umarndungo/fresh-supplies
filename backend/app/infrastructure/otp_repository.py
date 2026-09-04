from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import OTPCode
from app.domain.repositories import OTPRepository
from app.infrastructure.models import OTPCodeModel


def _to_entity(model: OTPCodeModel) -> OTPCode:
    return OTPCode(
        id=model.id,
        phone_number=model.phone_number,
        code=model.code,
        expires_at=model.expires_at,
        used=model.used,
        created_at=model.created_at,
    )


class SqlAlchemyOTPRepository(OTPRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_otp(self, *, phone_number: str, code: str, expires_at: datetime) -> None:
        model = OTPCodeModel(
            phone_number=phone_number,
            code=code,
            expires_at=expires_at,
        )
        self._session.add(model)
        await self._session.commit()

    async def get_latest_unused_otp(self, phone_number: str) -> OTPCode | None:
        result = await self._session.execute(
            select(OTPCodeModel)
            .where(OTPCodeModel.phone_number == phone_number, OTPCodeModel.used == False)
            .order_by(OTPCodeModel.created_at.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def mark_used(self, otp_id: UUID) -> None:
        model = await self._session.get(OTPCodeModel, otp_id)
        if model is None:
            return
        model.used = True
        await self._session.commit()

    async def count_recent_requests(self, phone_number: str, since: datetime) -> int:
        result = await self._session.execute(
            select(func.count(OTPCodeModel.id)).where(
                OTPCodeModel.phone_number == phone_number,
                OTPCodeModel.created_at >= since,
            )
        )
        return int(result.scalar() or 0)
