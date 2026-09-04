from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domain.entities import User, UserRole
from app.infrastructure.db import get_db_session
from app.api.deps import get_current_user, get_driver_service
from app.main import app

client = TestClient(app)


def _dummy_user():
    return User(
        id=uuid4(),
        email="driver@example.com",
        full_name="Test Driver",
        hashed_password="x",
        role=UserRole.FARMER_COOPERATIVE,
        organization_name=None,
        avatar_url=None,
        created_at=datetime.now(timezone.utc),
        phone_number="+254712345678",
        account_type=None,
        cooperative_id=None,
        phone_verified=True,
        profile_completed=True,
    )


@pytest.fixture(autouse=True)
def no_db():
    async def _dummy_db():
        yield None
    app.dependency_overrides[get_db_session] = _dummy_db
    yield
    app.dependency_overrides.pop(get_db_session, None)


@pytest.fixture()
def as_authenticated():
    async def _stub():
        return _dummy_user()
    app.dependency_overrides[get_current_user] = _stub
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def stub_driver_service():
    class StubDriverService:
        async def get_manifest(self, date, user_id, user_role):
            return [
                {
                    "shipment_id": str(uuid4()),
                    "owner_type": "INDIVIDUAL",
                    "cooperative_name": None,
                    "crop": "Tomatoes",
                    "quantity_kg": 50.0,
                    "pickup_location": {"lat": -1.29, "lon": 36.82},
                    "destination_market": "City Market",
                    "risk_tier": "FRESH",
                    "sequence": 1,
                }
            ]

        async def confirm_stop(self, shipment_id, confirmed_at, lat, lon):
            return {"status": "confirmed", "shipment_status": "DELIVERED"}

    app.dependency_overrides[get_driver_service] = lambda: StubDriverService()
    yield
    app.dependency_overrides.pop(get_driver_service, None)


# ── GET /manifest ───────────────────────────────────────────────────


def test_manifest_requires_auth():
    resp = client.get(
        "/api/v1/mobile/driver/manifest",
        params={"date": "2025-01-15T00:00:00Z"},
    )
    assert resp.status_code == 401, resp.text


def test_manifest_returns_stops(as_authenticated, stub_driver_service):
    resp = client.get(
        "/api/v1/mobile/driver/manifest",
        params={"date": "2025-01-15T00:00:00Z"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "stops" in body
    assert len(body["stops"]) == 1
    assert body["stops"][0]["crop"] == "Tomatoes"
    assert body["stops"][0]["riskTier"] == "FRESH"


# ── POST /stops/{id}/confirm ────────────────────────────────────────


def test_confirm_stop_requires_auth():
    shipment_id = str(uuid4())
    resp = client.post(
        f"/api/v1/mobile/driver/stops/{shipment_id}/confirm",
        json={
            "confirmedAt": "2025-01-15T14:30:00Z",
            "location": {"lat": -1.29, "lon": 36.82},
        },
    )
    assert resp.status_code == 401, resp.text


def test_confirm_stop_returns_status(as_authenticated, stub_driver_service):
    shipment_id = str(uuid4())
    resp = client.post(
        f"/api/v1/mobile/driver/stops/{shipment_id}/confirm",
        json={
            "confirmedAt": "2025-01-15T14:30:00Z",
            "location": {"lat": -1.29, "lon": 36.82},
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "confirmed"
    assert body["shipmentStatus"] == "DELIVERED"
