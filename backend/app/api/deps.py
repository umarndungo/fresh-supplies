from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth_service import AuthService
from app.application.device_service import DeviceService
from app.application.driver_service import DriverService
from app.application.mobile_auth_service import MobileAuthService
from app.application.mobile_recommendation_service import MobileRecommendationService
from app.application.mobile_shipment_service import MobileShipmentService
from app.application.otp_service import OTPService
from app.application.produce_service import ProduceService
from app.application.shipment_service import ShipmentService
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.domain.entities import User, UserRole
from app.infrastructure.cooperative_repository import SqlAlchemyCooperativeRepository
from app.infrastructure.db import get_db_session
from app.infrastructure.device_token_repository import SqlAlchemyDeviceTokenRepository
from app.infrastructure.driver_repository import SqlAlchemyDriverRepository
from app.infrastructure.otp_repository import SqlAlchemyOTPRepository
from app.infrastructure.produce_repository import SqlAlchemyProduceRepository
from app.infrastructure.shipment_repository import SqlAlchemyShipmentRepository
from app.infrastructure.shipment_sync_repository import SqlAlchemyShipmentSyncStagingRepository
from app.infrastructure.user_repository import SqlAlchemyUserRepository

# Registers the bearer-token security scheme in the OpenAPI schema so the
# Swagger UI shows an "Authorize" button for the protected routes below.
bearer_scheme = HTTPBearer(auto_error=False)


async def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(SqlAlchemyUserRepository(session))


async def get_shipment_service(session: AsyncSession = Depends(get_db_session)) -> ShipmentService:
    return ShipmentService(SqlAlchemyShipmentRepository(session))


async def get_produce_service(session: AsyncSession = Depends(get_db_session)) -> ProduceService:
    return ProduceService(SqlAlchemyProduceRepository(session))


async def get_otp_service(session: AsyncSession = Depends(get_db_session)) -> OTPService:
    return OTPService(SqlAlchemyOTPRepository(session))


async def get_device_service(session: AsyncSession = Depends(get_db_session)) -> DeviceService:
    return DeviceService(SqlAlchemyDeviceTokenRepository(session))


async def get_mobile_auth_service(session: AsyncSession = Depends(get_db_session)) -> MobileAuthService:
    user_repo = SqlAlchemyUserRepository(session)
    otp_repo = SqlAlchemyOTPRepository(session)
    coop_repo = SqlAlchemyCooperativeRepository(session)
    return MobileAuthService(user_repo, otp_repo, coop_repo)


async def get_mobile_shipment_service(session: AsyncSession = Depends(get_db_session)) -> MobileShipmentService:
    return MobileShipmentService(SqlAlchemyShipmentSyncStagingRepository(session))


async def get_mobile_recommendation_service(session: AsyncSession = Depends(get_db_session)) -> MobileRecommendationService:
    return MobileRecommendationService(SqlAlchemyShipmentRepository(session))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Missing bearer token.")

    token = credentials.credentials
    return await auth_service.get_current_user(token)


async def get_driver_service(session: AsyncSession = Depends(get_db_session)) -> DriverService:
    return DriverService(SqlAlchemyDriverRepository(session))


def require_roles(*roles: UserRole):
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenError("You do not have permission to perform this action.")
        return current_user

    return dependency
