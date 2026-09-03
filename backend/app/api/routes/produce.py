from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_produce_service
from app.application.produce_service import ProduceService
from app.application.schemas import CreateProduceRequest, ProduceOut, UpdateProduceRequest
from app.domain.entities import User

router = APIRouter(prefix="/produce", tags=["produce"])


@router.get("")
async def list_produce(
    _current_user: User = Depends(get_current_user),
    service: ProduceService = Depends(get_produce_service),
):
    produce = await service.list_produce()
    return {"data": [ProduceOut.model_validate(p).model_dump(by_alias=True) for p in produce]}


@router.post("", status_code=201)
async def create_produce(
    payload: CreateProduceRequest,
    current_user: User = Depends(get_current_user),
    service: ProduceService = Depends(get_produce_service),
):
    produce = await service.create_produce(
        actor=current_user,
        name=payload.name,
        variety=payload.variety,
        quantity_kg=payload.quantity_kg,
        unit_price=payload.unit_price,
        quality_grade=payload.quality_grade,
        harvest_date=payload.harvest_date,
        storage_location=payload.storage_location,
        commodity_class=payload.commodity_class,
    )
    return {"data": ProduceOut.model_validate(produce).model_dump(by_alias=True)}


@router.get("/{produce_id}")
async def get_produce(
    produce_id: UUID,
    _current_user: User = Depends(get_current_user),
    service: ProduceService = Depends(get_produce_service),
):
    produce = await service.get_produce(produce_id)
    return {"data": ProduceOut.model_validate(produce).model_dump(by_alias=True)}


@router.patch("/{produce_id}")
async def update_produce(
    produce_id: UUID,
    payload: UpdateProduceRequest,
    current_user: User = Depends(get_current_user),
    service: ProduceService = Depends(get_produce_service),
):
    produce = await service.update_produce(
        produce_id,
        actor=current_user,
        name=payload.name,
        variety=payload.variety,
        quantity_kg=payload.quantity_kg,
        unit_price=payload.unit_price,
        quality_grade=payload.quality_grade,
        harvest_date=payload.harvest_date,
        storage_location=payload.storage_location,
        commodity_class=payload.commodity_class,
        status=payload.status,
    )
    return {"data": ProduceOut.model_validate(produce).model_dump(by_alias=True)}


@router.delete("/{produce_id}", status_code=204)
async def delete_produce(
    produce_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProduceService = Depends(get_produce_service),
) -> None:
    await service.delete_produce(produce_id, actor=current_user)