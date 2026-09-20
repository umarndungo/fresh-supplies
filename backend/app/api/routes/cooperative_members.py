from fastapi import APIRouter, Depends

from app.api.deps import get_cooperative_member_service, require_cooperative_admin
from app.application.cooperative_member_service import CooperativeMemberService
from app.application.schemas import AdminUserOut, CreateCooperativeMemberRequest
from app.domain.entities import User

# Self-service member/driver provisioning for a cooperative admin, scoped to
# their own cooperative — see CooperativeMemberService.
router = APIRouter(
    prefix="/cooperative/members",
    tags=["cooperative-members"],
    dependencies=[Depends(require_cooperative_admin)],
)


@router.get("")
async def list_members(
    current_user: User = Depends(require_cooperative_admin),
    service: CooperativeMemberService = Depends(get_cooperative_member_service),
):
    members = await service.list_members(actor=current_user)
    return {"data": [AdminUserOut.model_validate(m).model_dump(by_alias=True) for m in members]}


@router.post("", status_code=201)
async def create_member(
    payload: CreateCooperativeMemberRequest,
    current_user: User = Depends(require_cooperative_admin),
    service: CooperativeMemberService = Depends(get_cooperative_member_service),
):
    user = await service.create_member(
        actor=current_user,
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
    )
    return {"data": AdminUserOut.model_validate(user).model_dump(by_alias=True)}
