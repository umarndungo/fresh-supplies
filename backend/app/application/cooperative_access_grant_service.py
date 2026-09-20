from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.domain.entities import CooperativeAccessGrant, User, UserRole
from app.domain.repositories import CooperativeAccessGrantRepository, CooperativeRepository, UserRepository

_VALID_GRANTEE_ROLES = {UserRole.LOGISTICS_MANAGER, UserRole.MARKET_ANALYST}


class CooperativeAccessGrantService:
    """Only ADMINISTRATOR may grant/revoke cooperative access — see
    backend/docs/multitenancy_design.md §2.4/§7.3. Rejecting ADMINISTRATOR as
    a grantee here (not just relying on nobody trying it) is what keeps
    "just grant the admin access" from becoming a backdoor around the
    platform-role rule in tenancy.require_not_administrator."""

    def __init__(
        self,
        grants: CooperativeAccessGrantRepository,
        users: UserRepository,
        cooperatives: CooperativeRepository,
    ):
        self._grants = grants
        self._users = users
        self._cooperatives = cooperatives

    def _ensure_administrator(self, actor: User) -> None:
        if actor.role != UserRole.ADMINISTRATOR:
            raise ForbiddenError("Only administrators can manage cooperative access grants.")

    async def grant(self, *, actor: User, user_id: UUID, cooperative_id: UUID) -> CooperativeAccessGrant:
        self._ensure_administrator(actor)
        target = await self._users.get_by_id(user_id)
        if not target:
            raise NotFoundError("User not found.")
        if target.role not in _VALID_GRANTEE_ROLES:
            raise ValidationError("Only logistics managers and market analysts can be granted cooperative access.")
        if not await self._cooperatives.get_by_id(cooperative_id):
            raise NotFoundError("Cooperative not found.")
        try:
            return await self._grants.create(user_id=user_id, cooperative_id=cooperative_id, granted_by=actor.id)
        except IntegrityError as exc:
            raise ConflictError("This user already has access to this cooperative.") from exc

    async def revoke(self, grant_id: UUID, *, actor: User) -> None:
        self._ensure_administrator(actor)
        if not await self._grants.delete(grant_id):
            raise NotFoundError("Grant not found.")

    async def list_for_cooperative(self, cooperative_id: UUID, *, actor: User) -> list[CooperativeAccessGrant]:
        self._ensure_administrator(actor)
        return await self._grants.list_for_cooperative(cooperative_id)
