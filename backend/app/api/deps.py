from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth_service import AuthService
from app.application.admin_service import AdminService
from app.application.admin_tenant_service import AdminTenantService
from app.application.cooperative_access_grant_service import CooperativeAccessGrantService
from app.application.cooperative_member_service import CooperativeMemberService
from app.application.device_service import DeviceService
from app.application.driver_service import DriverService
from app.application.mobile_auth_service import MobileAuthService
from app.application.mobile_recommendation_service import MobileRecommendationService
from app.application.mobile_shipment_service import MobileShipmentService
from app.application.otp_service import OTPService
from app.application.produce_service import ProduceService
from app.application.shipment_service import ShipmentService
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.domain.entities import CooperativeRole, User, UserRole
from app.infrastructure.cooperative_access_grant_repository import SqlAlchemyCooperativeAccessGrantRepository
from app.infrastructure.cooperative_repository import SqlAlchemyCooperativeRepository
from app.infrastructure.db import get_db_session
from app.infrastructure.device_token_repository import SqlAlchemyDeviceTokenRepository
from app.infrastructure.driver_repository import SqlAlchemyDriverRepository
from app.infrastructure.otp_repository import SqlAlchemyOTPRepository
from app.infrastructure.produce_repository import SqlAlchemyProduceRepository
from app.infrastructure.shipment_repository import SqlAlchemyShipmentRepository
from app.infrastructure.shipment_sync_repository import SqlAlchemyShipmentSyncStagingRepository
from app.infrastructure.tenant_usage_repository import SqlAlchemyTenantUsageRepository
from app.infrastructure.user_repository import SqlAlchemyUserRepository

# Registers the bearer-token security scheme in the OpenAPI schema so the
# Swagger UI shows an "Authorize" button for the protected routes below.
bearer_scheme = HTTPBearer(auto_error=False)


async def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(SqlAlchemyUserRepository(session))


async def get_shipment_service(session: AsyncSession = Depends(get_db_session)) -> ShipmentService:
    return ShipmentService(
        SqlAlchemyShipmentRepository(session),
        SqlAlchemyCooperativeAccessGrantRepository(session),
        SqlAlchemyUserRepository(session),
        SqlAlchemyProduceRepository(session),
    )


async def get_produce_service(session: AsyncSession = Depends(get_db_session)) -> ProduceService:
    return ProduceService(SqlAlchemyProduceRepository(session), SqlAlchemyCooperativeAccessGrantRepository(session))


async def get_otp_service(session: AsyncSession = Depends(get_db_session)) -> OTPService:
    return OTPService(SqlAlchemyOTPRepository(session))


async def get_device_service(session: AsyncSession = Depends(get_db_session)) -> DeviceService:
    return DeviceService(SqlAlchemyDeviceTokenRepository(session))


async def get_mobile_auth_service(session: AsyncSession = Depends(get_db_session)) -> MobileAuthService:
    return MobileAuthService(SqlAlchemyUserRepository(session), SqlAlchemyOTPRepository(session))


async def get_mobile_shipment_service(session: AsyncSession = Depends(get_db_session)) -> MobileShipmentService:
    return MobileShipmentService(SqlAlchemyShipmentSyncStagingRepository(session))


async def get_mobile_recommendation_service(session: AsyncSession = Depends(get_db_session)) -> MobileRecommendationService:
    return MobileRecommendationService(
        SqlAlchemyShipmentRepository(session), SqlAlchemyCooperativeAccessGrantRepository(session)
    )


async def get_admin_service(session: AsyncSession = Depends(get_db_session)) -> AdminService:
    return AdminService(SqlAlchemyUserRepository(session), SqlAlchemyCooperativeRepository(session))


async def get_admin_tenant_service(session: AsyncSession = Depends(get_db_session)) -> AdminTenantService:
    return AdminTenantService(
        SqlAlchemyCooperativeRepository(session),
        SqlAlchemyTenantUsageRepository(session),
        SqlAlchemyUserRepository(session),
    )


async def get_cooperative_member_service(session: AsyncSession = Depends(get_db_session)) -> CooperativeMemberService:
    return CooperativeMemberService(SqlAlchemyUserRepository(session))


async def get_cooperative_access_grant_service(
    session: AsyncSession = Depends(get_db_session),
) -> CooperativeAccessGrantService:
    return CooperativeAccessGrantService(
        SqlAlchemyCooperativeAccessGrantRepository(session),
        SqlAlchemyUserRepository(session),
        SqlAlchemyCooperativeRepository(session),
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Missing bearer token.")

    token = credentials.credentials
    return await auth_service.get_current_user(token)


async def get_driver_service(session: AsyncSession = Depends(get_db_session)) -> DriverService:
    return DriverService(SqlAlchemyDriverRepository(session), SqlAlchemyCooperativeAccessGrantRepository(session))


def require_roles(*roles: UserRole):
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenError("You do not have permission to perform this action.")
        return current_user

    return dependency


async def require_cooperative_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.FARMER_COOPERATIVE or current_user.cooperative_role != CooperativeRole.ADMIN:
        raise ForbiddenError("Only a cooperative admin can manage cooperative members.")
    return current_user
