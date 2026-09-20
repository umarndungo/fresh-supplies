import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import NotFoundError

from app.application.mobile_shipment_service import MobileShipmentService
from app.domain.entities import (
    OwnerType,
    ReconciliationStatus,
    ShipmentSyncStaging,
    User,
    UserRole,
)


run = asyncio.run


def _user(**overrides) -> User:
    defaults = dict(
        id=uuid4(),
        email="farmer@example.com",
        full_name="Test Farmer",
        hashed_password="x",
        role=UserRole.FARMER_COOPERATIVE,
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


def _staging(client_id: str, submitted_by_user_id) -> ShipmentSyncStaging:
    return ShipmentSyncStaging(
        id=uuid4(),
        client_id=client_id,
        crop="Tomatoes",
        quantity_kg=50.0,
        captured_at=datetime.now(timezone.utc),
        location_lat=-1.29,
        location_lon=36.82,
        photo_ref=None,
        photo_status=None,
        notes=None,
        owner_type=OwnerType.INDIVIDUAL,
        cooperative_id=None,
        submitted_by_user_id=submitted_by_user_id,
        sync_received_at=datetime.now(timezone.utc),
        reconciliation_status=ReconciliationStatus.PENDING,
        reconciled_shipment_id=None,
    )


class FakeStagingRepository:
    """Simulates a retried mobile sync racing a concurrent insert of the
    same client_id: get_by_client_id finds nothing (not committed by the
    other request yet), create() then hits the unique constraint."""

    def __init__(self, *, race_on_create: set[str] = frozenset()):
        self._by_client_id: dict[str, ShipmentSyncStaging] = {}
        self._race_on_create = set(race_on_create)
        self.rollback_calls = 0
        self.create_calls = 0

    async def get_by_client_id(self, client_id: str) -> ShipmentSyncStaging | None:
        return self._by_client_id.get(client_id)

    async def create(self, **kwargs) -> ShipmentSyncStaging:
        self.create_calls += 1
        client_id = kwargs["client_id"]
        if client_id in self._race_on_create:
            raise IntegrityError("duplicate client_id", {}, Exception("uq_shipment_sync_staging_client_id"))
        staging = _staging(client_id, kwargs["submitted_by_user_id"])
        self._by_client_id[client_id] = staging
        return staging

    async def rollback(self) -> None:
        self.rollback_calls += 1

    async def update_photo_ref(self, client_id: str, photo_ref: str) -> None:
        raise NotImplementedError

    async def list_since(self, since, user_id=None, cooperative_id=None):
        raise NotImplementedError

    async def list_pending_reconciliation(self, limit: int = 50):
        raise NotImplementedError


_ITEM = {
    "client_id": "c1",
    "crop": "Tomatoes",
    "quantity_kg": 50.0,
    "captured_at": datetime.now(timezone.utc),
    "location": {"lat": -1.29, "lon": 36.82},
    "photo_ref": None,
    "notes": None,
}


def test_sync_creates_new_item():
    repo = FakeStagingRepository()
    service = MobileShipmentService(repo)
    results = run(service.sync_shipments([_ITEM], user=_user()))
    assert results[0]["status"] == "created"
    assert repo.create_calls == 1
    assert repo.rollback_calls == 0


def test_sync_returns_duplicate_when_already_synced():
    repo = FakeStagingRepository()
    service = MobileShipmentService(repo)
    run(service.sync_shipments([_ITEM], user=_user()))
    results = run(service.sync_shipments([_ITEM], user=_user()))
    assert results[0]["status"] == "duplicate"
    assert repo.create_calls == 1  # second call never reaches create()


def test_upload_photo_rejects_client_id_owned_by_another_user():
    owner = _user()
    other_user = _user()
    repo = FakeStagingRepository()
    service = MobileShipmentService(repo)
    run(service.sync_shipments([_ITEM], user=owner))

    with pytest.raises(NotFoundError):
        run(service.upload_photo(client_id="c1", file=None, user=other_user))


def test_upload_photo_rejects_unknown_client_id():
    repo = FakeStagingRepository()
    service = MobileShipmentService(repo)

    with pytest.raises(NotFoundError):
        run(service.upload_photo(client_id="does-not-exist", file=None, user=_user()))


def test_sync_handles_concurrent_retry_race_as_duplicate_not_500():
    # get_by_client_id says "not seen yet" (the concurrent insert hasn't
    # committed when this request checks), but create() hits the unique
    # constraint set up by that concurrent insert winning the race.
    repo = FakeStagingRepository(race_on_create={"c1"})
    service = MobileShipmentService(repo)
    results = run(service.sync_shipments([_ITEM, {**_ITEM, "client_id": "c2"}], user=_user()))

    assert results[0]["status"] == "duplicate"
    assert results[0]["client_id"] == "c1"
    assert repo.rollback_calls == 1
    # The session must be usable again for the rest of the batch.
    assert results[1]["status"] == "created"
    assert results[1]["client_id"] == "c2"
