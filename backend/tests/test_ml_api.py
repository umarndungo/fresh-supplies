"""API endpoint tests for the ML routes (FastAPI TestClient).

These assert the security + response-contract behaviour of /ml endpoints:

  - /health is public
  - /ml/predict-spoilage and /ml/recommend-market REQUIRE a bearer token (401
    without one) and return the documented response shape when authenticated.

The authenticated path overrides get_current_user with a stub so the test does
not need a live database; the 401 path overrides get_db_session with a dummy
session so the dependency graph resolves without connecting to Postgres.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domain.entities import User, UserRole
from app.infrastructure.db import get_db_session
from app.api.deps import get_current_user
from app.main import app

client = TestClient(app)


def _dummy_user():
    return User(
        id=uuid4(),
        email="analyst@example.com",
        full_name="Test Analyst",
        hashed_password="x",
        role=UserRole.MARKET_ANALYST,
        organization_name="Test Coop",
        avatar_url=None,
        created_at=datetime.now(timezone.utc),
        phone_number=None,
        account_type=None,
        cooperative_id=None,
        phone_verified=False,
        profile_completed=True,
    )


@pytest.fixture(autouse=True)
def no_db_dependency():
    """The 401 path resolves get_auth_service -> get_db_session; stub it out."""
    async def _dummy_db():
        yield None
    app.dependency_overrides[get_db_session] = _dummy_db
    yield
    app.dependency_overrides.pop(get_db_session, None)


@pytest.fixture()
def as_authenticated():
    async def _stub_current_user():
        return _dummy_user()
    app.dependency_overrides[get_current_user] = _stub_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


SPOILAGE_PAYLOAD = {
    "crop_type": "Tomatoes",
    "latitude": -1.29,
    "longitude": 36.82,
    "Temperature_C": 30.0,
    "Transit_Duration_Hr": 8.0,
    "Pressure_PSI": 30.0,
    "baseline_loss_pct": 12.0,
    "quantity_kg": 100.0,
}


def test_health_is_public():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_predict_spoilage_requires_auth():
    resp = client.post("/api/v1/ml/predict-spoilage", json=SPOILAGE_PAYLOAD)
    assert resp.status_code == 401, resp.text


def test_recommend_market_requires_auth():
    payload = {**SPOILAGE_PAYLOAD, "top_n": 3}
    resp = client.post("/api/v1/ml/recommend-market", json=payload)
    assert resp.status_code == 401, resp.text


def test_predict_spoilage_authenticated(as_authenticated):
    resp = client.post("/api/v1/ml/predict-spoilage", json=SPOILAGE_PAYLOAD)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert {"spoilage_probability", "risk_tier", "spoil_prediction"} <= set(body)
    assert 0.0 <= body["spoilage_probability"] <= 1.0
    assert body["risk_tier"] in {"FRESH", "AT_RISK", "CRITICAL"}
    assert isinstance(body["spoil_prediction"], bool)
    assert body["spoil_prediction"] == (body["spoilage_probability"] >= 0.5)


def test_recommend_market_authenticated(as_authenticated):
    payload = {**SPOILAGE_PAYLOAD, "top_n": 5}
    resp = client.post("/api/v1/ml/recommend-market", json=payload)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert isinstance(body, list) and len(body) <= 5
    assert body, "should return at least one market for a known crop"
    keys = {"market_id", "market_name", "region", "distance_km",
            "price_per_kg", "spoilage_probability", "revenue_retained"}
    for row in body:
        assert keys <= set(row)
        assert row["revenue_retained"] > 0
        assert 0.0 <= row["spoilage_probability"] <= 1.0
    revs = [row["revenue_retained"] for row in body]
    assert revs == sorted(revs, reverse=True)


def test_recommend_market_unknown_crop_authed(as_authenticated):
    payload = {**SPOILAGE_PAYLOAD, "crop_type": "Durian", "top_n": 3}
    resp = client.post("/api/v1/ml/recommend-market", json=payload)
    assert resp.status_code == 422  # unknown crop -> clean MLServiceError response
    assert "message" in resp.json()
