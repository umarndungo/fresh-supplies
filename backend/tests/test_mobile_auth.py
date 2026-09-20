from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domain.entities import User, UserRole
from app.infrastructure.db import get_db_session
from app.api.deps import get_otp_service, get_mobile_auth_service
from app.main import app

client = TestClient(app)


def _dummy_user():
    return User(
        id=uuid4(),
        email="farmer@example.com",
        full_name="",
        hashed_password="x",
        role=UserRole.FARMER_COOPERATIVE,
        organization_name=None,
        avatar_url=None,
        created_at=datetime.now(timezone.utc),
        phone_number=None,
        account_type=None,
        cooperative_id=None,
        phone_verified=False,
        profile_completed=False,
    )


@pytest.fixture(autouse=True)
def no_db():
    async def _dummy_db():
        yield None
    app.dependency_overrides[get_db_session] = _dummy_db
    yield
    app.dependency_overrides.pop(get_db_session, None)


@pytest.fixture()
def stub_otp_service():
    class StubOTP:
        async def request_otp(self, email):
            return {"status": "sent", "expires_in_seconds": 300}

        async def verify_otp(self, email, code):
            return True

    app.dependency_overrides[get_otp_service] = lambda: StubOTP()
    yield
    app.dependency_overrides.pop(get_otp_service, None)


@pytest.fixture()
def stub_mobile_auth():
    class StubMobileAuth:
        async def otp_login(self, email):
            user = _dummy_user()
            return user, "fake.access.token", 900, "fake.refresh.token"

        async def refresh(self, refresh_token):
            user = _dummy_user()
            return user, "new.access.token", 900, "new.refresh.token"

    app.dependency_overrides[get_mobile_auth_service] = lambda: StubMobileAuth()
    yield
    app.dependency_overrides.pop(get_mobile_auth_service, None)


# ── OTP /request ────────────────────────────────────────────────────


def test_otp_request_returns_sent(stub_otp_service):
    resp = client.post(
        "/api/v1/mobile/auth/otp/request",
        json={"email": "farmer@example.com"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "sent"
    assert body["expires_in_seconds"] == 300


def test_otp_request_requires_email():
    resp = client.post("/api/v1/mobile/auth/otp/request", json={})
    assert resp.status_code == 422


def test_otp_request_rejects_invalid_email():
    resp = client.post("/api/v1/mobile/auth/otp/request", json={"email": "not-an-email"})
    assert resp.status_code == 422


# ── OTP /verify ─────────────────────────────────────────────────────


def test_otp_verify_returns_tokens(stub_otp_service, stub_mobile_auth):
    resp = client.post(
        "/api/v1/mobile/auth/otp/verify",
        json={"email": "farmer@example.com", "code": "123456"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["accessToken"] == "fake.access.token"
    assert data["refreshToken"] == "fake.refresh.token"
    assert data["expiresIn"] == 900
    assert "user" in data
    assert data["user"]["email"] == "farmer@example.com"


def test_otp_verify_requires_code(stub_otp_service):
    resp = client.post(
        "/api/v1/mobile/auth/otp/verify",
        json={"email": "farmer@example.com"},
    )
    assert resp.status_code == 422


# ── /refresh ────────────────────────────────────────────────────────


def test_refresh_returns_new_tokens(stub_mobile_auth):
    resp = client.post(
        "/api/v1/mobile/auth/refresh",
        json={"refreshToken": "old.refresh.token"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["accessToken"] == "new.access.token"
    assert data["refreshToken"] == "new.refresh.token"
    assert data["expiresIn"] == 900
    assert "user" in data


def test_refresh_requires_token():
    resp = client.post("/api/v1/mobile/auth/refresh", json={})
    assert resp.status_code == 422
