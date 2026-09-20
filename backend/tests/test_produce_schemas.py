"""Regression test for a real bug hit against a live stack: ProduceOut
required cooperative_id as a UUID, but produce.cooperative_id is legitimately
None for an INDIVIDUAL/solo-owned item (backend/docs/multitenancy_design.md
§2.1) — every produce creation/list call for a solo farmer 500'd until this
was fixed. No DB needed; this just exercises the Pydantic schema directly."""

from datetime import datetime, timezone
from uuid import uuid4

from app.application.schemas import ProduceOut
from app.domain.entities import CommodityClass, OwnerType, ProduceItem, ProduceStatus


def _produce_item(*, owner_type: OwnerType, cooperative_id=None) -> ProduceItem:
    return ProduceItem(
        id=uuid4(),
        name="Tomatoes",
        variety="Roma",
        quantity_kg=100.0,
        unit_price=90.0,
        quality_grade="A",
        harvest_date=datetime.now(timezone.utc),
        storage_location="Warehouse 1",
        commodity_class=CommodityClass.PERISHABLE,
        owner_type=owner_type,
        created_by=uuid4(),
        status=ProduceStatus.AVAILABLE,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        cooperative_id=cooperative_id,
    )


def test_produce_out_serializes_individual_owned_item_with_null_cooperative_id():
    item = _produce_item(owner_type=OwnerType.INDIVIDUAL, cooperative_id=None)
    out = ProduceOut.model_validate(item).model_dump(by_alias=True)
    assert out["cooperativeId"] is None
    assert out["ownerType"] == "INDIVIDUAL"
    assert out["createdBy"] == item.created_by


def test_produce_out_serializes_cooperative_owned_item_with_real_cooperative_id():
    coop_id = uuid4()
    item = _produce_item(owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id)
    out = ProduceOut.model_validate(item).model_dump(by_alias=True)
    assert out["cooperativeId"] == coop_id
    assert out["ownerType"] == "COOPERATIVE"
