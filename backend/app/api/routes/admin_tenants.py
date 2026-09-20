from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_admin_tenant_service, get_cooperative_access_grant_service, get_current_user, require_roles
from app.application.admin_tenant_service import AdminTenantService
from app.application.cooperative_access_grant_service import CooperativeAccessGrantService
from app.application.schemas import (
    CreateGrantRequest,
    CreateTenantRequest,
    GrantOut,
    TenantOut,
    TenantUsageOut,
    UpdateTenantRequest,
)
from app.domain.entities import User, UserRole

# Tenant lifecycle + billing usage + cooperative access grants — ADMINISTRATOR
# only, and deliberately separate from /shipments and /produce: this router
# never touches shipment/produce content, only cooperative metadata and
# aggregate counts. See backend/docs/multitenancy_design.md §7.
router = APIRouter(
    prefix="/admin",
    tags=["admin-tenants"],
    dependencies=[Depends(require_roles(UserRole.ADMINISTRATOR))],
)


@router.post("/tenants", status_code=201)
async def create_tenant(
    payload: CreateTenantRequest,
    current_user: User = Depends(get_current_user),
    service: AdminTenantService = Depends(get_admin_tenant_service),
):
    tenant = await service.create_tenant(
        actor=current_user,
        name=payload.name,
        admin_email=payload.admin_email,
        admin_full_name=payload.admin_full_name,
    )
    return {"data": TenantOut.model_validate(tenant).model_dump(by_alias=True)}


@router.get("/tenants")
async def list_tenants(
    current_user: User = Depends(get_current_user),
    service: AdminTenantService = Depends(get_admin_tenant_service),
):
    tenants = await service.list_tenants(actor=current_user)
    return {"data": [TenantOut.model_validate(t).model_dump(by_alias=True) for t in tenants]}


@router.patch("/tenants/{cooperative_id}")
async def update_tenant(
    cooperative_id: UUID,
    payload: UpdateTenantRequest,
    current_user: User = Depends(get_current_user),
    service: AdminTenantService = Depends(get_admin_tenant_service),
):
    tenant = await service.update_tenant(cooperative_id, actor=current_user, name=payload.name)
    return {"data": TenantOut.model_validate(tenant).model_dump(by_alias=True)}


@router.get("/tenants/usage")
async def list_tenant_usage(
    current_user: User = Depends(get_current_user),
    service: AdminTenantService = Depends(get_admin_tenant_service),
):
    usage = await service.list_tenant_usage(actor=current_user)
    return {"data": [TenantUsageOut.model_validate(u).model_dump(by_alias=True) for u in usage]}


@router.get("/tenants/{cooperative_id}/usage")
async def get_tenant_usage(
    cooperative_id: UUID,
    current_user: User = Depends(get_current_user),
    service: AdminTenantService = Depends(get_admin_tenant_service),
):
    usage = await service.get_tenant_usage(cooperative_id, actor=current_user)
    return {"data": TenantUsageOut.model_validate(usage).model_dump(by_alias=True)}


@router.post("/grants", status_code=201)
async def create_grant(
    payload: CreateGrantRequest,
    current_user: User = Depends(get_current_user),
    service: CooperativeAccessGrantService = Depends(get_cooperative_access_grant_service),
):
    grant = await service.grant(actor=current_user, user_id=payload.user_id, cooperative_id=payload.cooperative_id)
    return {"data": GrantOut.model_validate(grant).model_dump(by_alias=True)}


@router.get("/tenants/{cooperative_id}/grants")
async def list_grants_for_tenant(
    cooperative_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CooperativeAccessGrantService = Depends(get_cooperative_access_grant_service),
):
    grants = await service.list_for_cooperative(cooperative_id, actor=current_user)
    return {"data": [GrantOut.model_validate(g).model_dump(by_alias=True) for g in grants]}


@router.delete("/grants/{grant_id}", status_code=204)
async def revoke_grant(
    grant_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CooperativeAccessGrantService = Depends(get_cooperative_access_grant_service),
) -> None:
    await service.revoke(grant_id, actor=current_user)
