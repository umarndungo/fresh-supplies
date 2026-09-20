from uuid import UUID

from fastapi.concurrency import run_in_threadpool

from app.core.email_sender import send_invite_email
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.domain.entities import Cooperative, CooperativeRole, User, UserRole
from app.domain.repositories import CooperativeRepository, TenantUsageRepository, UserRepository


class AdminTenantService:
    """Tenant lifecycle + aggregate billing usage for ADMINISTRATOR — see
    backend/docs/multitenancy_design.md §7. This service never touches
    ShipmentRepository/ProduceRepository, only Cooperative metadata and
    TenantUsageRepository's aggregate counts — it structurally cannot return
    shipment/produce row content."""

    def __init__(
        self,
        cooperatives: CooperativeRepository,
        usage: TenantUsageRepository,
        users: UserRepository,
    ):
        self._cooperatives = cooperatives
        self._usage = usage
        self._users = users

    def _ensure_administrator(self, actor: User) -> None:
        if actor.role != UserRole.ADMINISTRATOR:
            raise ForbiddenError("Only administrators manage tenants.")

    async def create_tenant(
        self,
        *,
        actor: User,
        name: str,
        admin_email: str | None = None,
        admin_full_name: str | None = None,
    ) -> Cooperative:
        self._ensure_administrator(actor)

        if admin_email is not None:
            existing = await self._users.get_by_email(admin_email)
            if existing:
                raise ConflictError("An account with this email already exists.", field="adminEmail")

        cooperative = await self._cooperatives.create(name=name, created_by=actor.id)

        if admin_email is not None:
            await self._users.create_pending(
                email=admin_email,
                full_name=admin_full_name or "",
                role=UserRole.FARMER_COOPERATIVE,
                organization_name=None,
                cooperative_id=cooperative.id,
                cooperative_role=CooperativeRole.ADMIN,
            )
            await run_in_threadpool(
                send_invite_email, admin_email, admin_full_name or "", UserRole.FARMER_COOPERATIVE.value
            )

        return cooperative

    async def list_tenants(self, *, actor: User) -> list[Cooperative]:
        self._ensure_administrator(actor)
        return await self._cooperatives.list_all()

    async def update_tenant(self, cooperative_id: UUID, *, actor: User, name: str | None = None) -> Cooperative:
        self._ensure_administrator(actor)
        updated = await self._cooperatives.update(cooperative_id, name=name)
        if not updated:
            raise NotFoundError("Tenant not found.")
        return updated

    async def get_tenant_usage(self, cooperative_id: UUID, *, actor: User) -> dict:
        self._ensure_administrator(actor)
        if not await self._cooperatives.get_by_id(cooperative_id):
            raise NotFoundError("Tenant not found.")
        return await self._usage.get_cooperative_usage(cooperative_id)

    async def list_tenant_usage(self, *, actor: User) -> list[dict]:
        self._ensure_administrator(actor)
        return await self._usage.list_cooperative_usage()
