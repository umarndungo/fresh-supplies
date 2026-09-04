from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domain.entities import User, UserRole
from app.infrastructure.db import get_db_session
from app.api.deps import get_current_user, get_device_service
from app.main import app

client = TestClient(app)


def _dummy_user():
    return User(
        id=uuid4(),
        email="user@example.com",
        full_name="Test User",
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
def stub_device_service():
    class StubDeviceService:
        async def register_device(self, user_id, device_token, platform):
            return {"status": "registered"}

    app.dependency_overrides[get_device_service] = lambda: StubDeviceService()
    yield
    app.dependency_overrides.pop(get_device_service, None)


# ── POST /register ──────────────────────────────────────────────────


def test_register_device_requires_auth():
    resp = client.post(
        "/api/v1/mobile/devices/register",
        json={"deviceToken": "fcm-token-123", "platform": "android"},
    )
    assert resp.status_code == 401, resp.text


def test_register_device_returns_registered(as_authenticated, stub_device_service):
    resp = client.post(
        "/api/v1/mobile/devices/register",
        json={"deviceToken": "fcm-token-123", "platform": "android"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "registered"
