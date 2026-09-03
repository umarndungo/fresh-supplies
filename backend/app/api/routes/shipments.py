from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_shipment_service
from app.application.schemas import CreateShipmentRequest, ShipmentOut, UpdateShipmentRequest
from app.application.shipment_service import ShipmentService
from app.domain.entities import User

router = APIRouter(prefix="/shipments", tags=["shipments"])


@router.get("")
async def list_shipments(
    _current_user: User = Depends(get_current_user),
    service: ShipmentService = Depends(get_shipment_service),
):
    shipments = await service.list_shipments()
    return {"data": [ShipmentOut.model_validate(s).model_dump(by_alias=True) for s in shipments]}


@router.post("", status_code=201)
async def create_shipment(
    payload: CreateShipmentRequest,
    current_user: User = Depends(get_current_user),
    service: ShipmentService = Depends(get_shipment_service),
):
    shipment = await service.create_shipment(
        actor=current_user,
        origin=payload.origin,
        destination=payload.destination,
        produce_type=payload.produce_type,
        scheduled_date=payload.scheduled_date,
    )
    return {"data": ShipmentOut.model_validate(shipment).model_dump(by_alias=True)}


@router.get("/{shipment_id}")
async def get_shipment(
    shipment_id: UUID,
    _current_user: User = Depends(get_current_user),
    service: ShipmentService = Depends(get_shipment_service),
):
    shipment = await service.get_shipment(shipment_id)
    return {"data": ShipmentOut.model_validate(shipment).model_dump(by_alias=True)}


@router.patch("/{shipment_id}")
async def update_shipment(
    shipment_id: UUID,
    payload: UpdateShipmentRequest,
    current_user: User = Depends(get_current_user),
    service: ShipmentService = Depends(get_shipment_service),
):
    shipment = await service.update_shipment(
        shipment_id, actor=current_user, status=payload.status, delivery_date=payload.delivery_date
    )
    return {"data": ShipmentOut.model_validate(shipment).model_dump(by_alias=True)}


@router.delete("/{shipment_id}", status_code=204)
async def delete_shipment(
    shipment_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ShipmentService = Depends(get_shipment_service),
) -> None:
    await service.delete_shipment(shipment_id, actor=current_user)
