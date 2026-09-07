from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_admin_service, require_roles
from app.application.admin_service import AdminService
from app.application.schemas import (
    AdminCreateUserRequest,
    AdminUpdateUserRequest,
    AdminUserOut,
)
from app.domain.entities import User, UserRole

# User administration is restricted to the ADMINISTRATOR role. All responses
# follow the rest of the API's { "data": ... } envelope convention.
router = APIRouter(
    prefix="/admin/users",
    tags=["admin"],
    dependencies=[Depends(require_roles(UserRole.ADMINISTRATOR))],
)


def _serialize(user: User) -> dict:
    return AdminUserOut.model_validate(user).model_dump(by_alias=True)


@router.get("")
async def list_users(service: AdminService = Depends(get_admin_service)):
    users = await service.list_users()
    return {"data": [_serialize(u) for u in users]}


@router.post("", status_code=201)
async def create_user(
    payload: AdminCreateUserRequest,
    service: AdminService = Depends(get_admin_service),
):
    user = await service.create_user(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role=payload.role,
        organization_name=payload.organization_name,
    )
    return {"data": _serialize(user)}


@router.patch("/{user_id}")
async def update_user(
    user_id: UUID,
    payload: AdminUpdateUserRequest,
    service: AdminService = Depends(get_admin_service),
):
    user = await service.update_user(
        user_id,
        full_name=payload.full_name,
        organization_name=payload.organization_name,
        role=payload.role,
        is_active=payload.is_active,
        reset_password=payload.reset_password,
    )
    return {"data": _serialize(user)}


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR)),
    service: AdminService = Depends(get_admin_service),
) -> None:
    await service.delete_user(user_id, actor_id=current_user.id)