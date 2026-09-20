from fastapi.concurrency import run_in_threadpool

from app.core.email_sender import send_invite_email
from app.core.exceptions import ConflictError, ForbiddenError, ValidationError
from app.domain.entities import CooperativeRole, User, UserRole
from app.domain.repositories import UserRepository

# A cooperative admin may only add members/drivers to their OWN cooperative.
_ALLOWED_ROLES = {UserRole.FARMER_COOPERATIVE, UserRole.DRIVER}


class CooperativeMemberService:
    """Lets a cooperative admin (FARMER_COOPERATIVE + cooperative_role=ADMIN)
    provision members and drivers scoped to their own cooperative — the
    self-service counterpart to AdminService.create_user for platform staff.
    cooperative_id/cooperative_role are always derived from the actor, never
    taken from the request, so a cooperative admin cannot add anyone to a
    different cooperative."""

    def __init__(self, user_repository: UserRepository):
        self._users = user_repository

    def _ensure_cooperative_admin(self, actor: User) -> None:
        if actor.role != UserRole.FARMER_COOPERATIVE or actor.cooperative_role != CooperativeRole.ADMIN:
            raise ForbiddenError("Only a cooperative admin can manage cooperative members.")
        if actor.cooperative_id is None:
            raise ForbiddenError("Your account is not attached to a cooperative.")

    async def create_member(self, *, actor: User, email: str, full_name: str, role: UserRole) -> User:
        self._ensure_cooperative_admin(actor)
        if role not in _ALLOWED_ROLES:
            raise ValidationError("role must be FARMER_COOPERATIVE or DRIVER.")

        existing = await self._users.get_by_email(email)
        if existing:
            raise ConflictError("An account with this email already exists.", field="email")

        cooperative_role = CooperativeRole.MEMBER if role == UserRole.FARMER_COOPERATIVE else None
        user = await self._users.create_pending(
            email=email,
            full_name=full_name,
            role=role,
            organization_name=None,
            cooperative_id=actor.cooperative_id,
            cooperative_role=cooperative_role,
        )
        await run_in_threadpool(send_invite_email, email, full_name, role.value)
        return user

    async def list_members(self, *, actor: User) -> list[User]:
        self._ensure_cooperative_admin(actor)
        return await self._users.list_by_cooperative(actor.cooperative_id)
