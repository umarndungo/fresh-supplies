from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domain.entities import User, UserRole
from app.infrastructure.db import get_db_session
from app.api.deps import (
    get_current_user,
    get_mobile_shipment_service,
    get_mobile_recommendation_service,
)
from app.main import app

client = TestClient(app)


def _dummy_user():
    return User(
        id=uuid4(),
        email="driver@example.com",
        full_name="Test Driver",
        hashed_password="x",
        role=UserRole.FARMER_COOPERATIVE,
        organization_name="Coop",
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
def stub_shipment_service():
    class StubShipmentService:
        async def sync_shipments(self, shipments, user):
            results = []
            for item in shipments:
                results.append({
                    "client_id": item["client_id"],
                    "status": "created",
                    "server_id": uuid4(),
                    "risk_tier": "FRESH",
                    "error": None,
                })
            return results

        async def upload_photo(self, client_id, file):
            return {"photo_ref": f"media/shipment_photos/{client_id}.jpg", "status": "uploaded"}

        async def get_sync_status(self, since, user):
            return []

    app.dependency_overrides[get_mobile_shipment_service] = lambda: StubShipmentService()
    yield
    app.dependency_overrides.pop(get_mobile_shipment_service, None)


@pytest.fixture()
def stub_recommendation_service():
    class StubRecommendationService:
        async def get_recommendation(self, shipment_id, crop, quantity_kg, lat, lon, locale="en"):
            return {
                "risk_tier": "FRESH",
                "risk_label": "Fresh",
                "recommended_market": {"name": "City Market", "distance_km": 5.0, "est_price_per_kg": 120, "est_revenue_retained": 11000},
                "alternate_markets": [],
            }

    app.dependency_overrides[get_mobile_recommendation_service] = lambda: StubRecommendationService()
    yield
    app.dependency_overrides.pop(get_mobile_recommendation_service, None)


_SHIPMENT_PAYLOAD = {
    "shipments": [
        {
            "clientId": "c1",
            "crop": "Tomatoes",
            "quantityKg": 50.0,
            "capturedAt": "2025-01-15T10:00:00Z",
            "location": {"lat": -1.29, "lon": 36.82},
            "photoRef": None,
            "notes": None,
        }
    ]
}


# ── POST /sync ──────────────────────────────────────────────────────


def test_sync_returns_results(as_authenticated, stub_shipment_service):
    resp = client.post("/api/v1/mobile/shipments/sync", json=_SHIPMENT_PAYLOAD)
    assert resp.status_code == 200, resp.text
    results = resp.json()["results"]
    assert isinstance(results, list) and len(results) == 1
    assert results[0]["status"] == "created"
    assert results[0]["riskTier"] == "FRESH"


def test_sync_empty_shipments_returns_empty(as_authenticated, stub_shipment_service):
    resp = client.post("/api/v1/mobile/shipments/sync", json={"shipments": []})
    assert resp.status_code == 200, resp.text
    assert resp.json()["results"] == []


def test_sync_requires_auth():
    resp = client.post("/api/v1/mobile/shipments/sync", json=_SHIPMENT_PAYLOAD)
    assert resp.status_code == 401, resp.text


# ── POST /photo-upload ──────────────────────────────────────────────


def test_photo_upload_requires_auth():
    resp = client.post("/api/v1/mobile/shipments/photo-upload")
    assert resp.status_code == 401, resp.text


# ── GET /sync-status ────────────────────────────────────────────────


def test_sync_status_requires_auth():
    resp = client.get(
        "/api/v1/mobile/shipments/sync-status",
        params={"since": "2025-01-01T00:00:00Z"},
    )
    assert resp.status_code == 401, resp.text


# ── GET /{id}/recommendation ────────────────────────────────────────


def test_recommendation_requires_auth():
    shipment_id = uuid4()
    resp = client.get(
        f"/api/v1/mobile/shipments/{shipment_id}/recommendation",
        params={
            "crop": "Tomatoes",
            "quantityKg": 50.0,
            "lat": -1.29,
            "lon": 36.82,
        },
    )
    assert resp.status_code == 401, resp.text


def test_recommendation_returns_data(as_authenticated, stub_recommendation_service):
    shipment_id = uuid4()
    resp = client.get(
        f"/api/v1/mobile/shipments/{shipment_id}/recommendation",
        params={
            "crop": "Tomatoes",
            "quantityKg": 50.0,
            "lat": -1.29,
            "lon": 36.82,
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["riskTier"] == "FRESH"
    assert body["riskLabel"] == "Fresh"
    assert body["recommendedMarket"]["name"] == "City Market"
