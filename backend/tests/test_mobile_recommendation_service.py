import asyncio
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from app.application.mobile_recommendation_service import MobileRecommendationService
from app.core.exceptions import ForbiddenError, NotFoundError
from app.domain.entities import OwnerType, Shipment, ShipmentStatus, User, UserRole

run = asyncio.run


def _user(role: UserRole, **overrides) -> User:
    defaults = dict(
        id=uuid4(),
        email="user@example.com",
        full_name="Test User",
        hashed_password="x",
        role=role,
        organization_name=None,
        avatar_url=None,
        created_at=datetime.now(timezone.utc),
        phone_number=None,
        account_type=None,
        cooperative_id=None,
        phone_verified=True,
        profile_completed=True,
    )
    defaults.update(overrides)
    return User(**defaults)


def _shipment(**overrides) -> Shipment:
    defaults = dict(
        id=uuid4(),
        origin="Kianyaga",
        destination="Nairobi",
        produce_type="Mangoes",
        status=ShipmentStatus.SCHEDULED,
        scheduled_date=datetime.now(timezone.utc),
        delivery_date=None,
        created_by=uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        cooperative_id=None,
        owner_type=OwnerType.INDIVIDUAL,
        driver_user_id=None,
    )
    defaults.update(overrides)
    return Shipment(**defaults)


class FakeShipmentRepository:
    def __init__(self, shipments: list[Shipment]):
        self._shipments = {s.id: s for s in shipments}

    async def get_by_id(self, shipment_id):
        return self._shipments.get(shipment_id)


class FakeGrantsRepository:
    def __init__(self, grants: dict[UUID, set[UUID]] | None = None):
        self._grants = grants or {}

    async def list_cooperative_ids_for(self, user_id):
        return list(self._grants.get(user_id, set()))


def test_manager_can_get_recommendation_for_granted_cooperative_shipment():
    coop_id = uuid4()
    manager = _user(UserRole.LOGISTICS_MANAGER)
    shipment = _shipment(owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id)
    service = MobileRecommendationService(
        FakeShipmentRepository([shipment]), FakeGrantsRepository({manager.id: {coop_id}})
    )

    result = run(
        service.get_recommendation(shipment.id, crop="Mangoes", quantity_kg=100, lat=-1.0, lon=37.0, actor=manager)
    )
    assert "risk_tier" in result


def test_manager_cannot_get_recommendation_for_ungranted_cooperative_shipment():
    manager = _user(UserRole.LOGISTICS_MANAGER)
    shipment = _shipment(owner_type=OwnerType.COOPERATIVE, cooperative_id=uuid4())
    service = MobileRecommendationService(FakeShipmentRepository([shipment]), FakeGrantsRepository())

    with pytest.raises(NotFoundError):
        run(
            service.get_recommendation(
                shipment.id, crop="Mangoes", quantity_kg=100, lat=-1.0, lon=37.0, actor=manager
            )
        )


def test_unknown_shipment_id_raises_not_found():
    manager = _user(UserRole.LOGISTICS_MANAGER)
    service = MobileRecommendationService(FakeShipmentRepository([]), FakeGrantsRepository())

    with pytest.raises(NotFoundError):
        run(
            service.get_recommendation(uuid4(), crop="Mangoes", quantity_kg=100, lat=-1.0, lon=37.0, actor=manager)
        )


def test_administrator_is_refused_entirely():
    admin = _user(UserRole.ADMINISTRATOR)
    shipment = _shipment(owner_type=OwnerType.INDIVIDUAL, created_by=admin.id)
    service = MobileRecommendationService(FakeShipmentRepository([shipment]), FakeGrantsRepository())

    with pytest.raises(ForbiddenError):
        run(
            service.get_recommendation(shipment.id, crop="Mangoes", quantity_kg=100, lat=-1.0, lon=37.0, actor=admin)
        )


def test_solo_farmer_can_get_recommendation_for_own_shipment():
    farmer = _user(UserRole.FARMER_COOPERATIVE)
    shipment = _shipment(owner_type=OwnerType.INDIVIDUAL, created_by=farmer.id)
    service = MobileRecommendationService(FakeShipmentRepository([shipment]), FakeGrantsRepository())

    result = run(
        service.get_recommendation(shipment.id, crop="Mangoes", quantity_kg=100, lat=-1.0, lon=37.0, actor=farmer)
    )
    assert "risk_tier" in result
