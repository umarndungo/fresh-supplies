from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domain.entities import User, UserRole
from app.infrastructure.db import get_db_session
from app.api.deps import get_current_user, get_otp_service, get_mobile_auth_service
from app.main import app

client = TestClient(app)


def _dummy_user():
    return User(
        id=uuid4(),
        email="",
        full_name="",
        hashed_password="x",
        role=UserRole.FARMER_COOPERATIVE,
        organization_name=None,
        avatar_url=None,
        created_at=datetime.now(timezone.utc),
        phone_number="+254712345678",
        account_type=None,
        cooperative_id=None,
        phone_verified=True,
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
        async def request_otp(self, phone_number):
            return {"status": "sent", "expires_in_seconds": 300}

        async def verify_otp(self, phone_number, code):
            return True

    app.dependency_overrides[get_otp_service] = lambda: StubOTP()
    yield
    app.dependency_overrides.pop(get_otp_service, None)


@pytest.fixture()
def stub_mobile_auth():
    class StubMobileAuth:
        async def otp_login(self, phone_number):
            user = _dummy_user()
            return user, "fake.access.token", 900, "fake.refresh.token"

        async def refresh(self, refresh_token):
            user = _dummy_user()
            return user, "new.access.token", 900, "new.refresh.token"

        async def complete_profile(self, user_id, **kwargs):
            user = _dummy_user()
            return {"user": user}

    app.dependency_overrides[get_mobile_auth_service] = lambda: StubMobileAuth()
    yield
    app.dependency_overrides.pop(get_mobile_auth_service, None)


@pytest.fixture()
def as_authenticated():
    async def _stub():
        return _dummy_user()
    app.dependency_overrides[get_current_user] = _stub
    yield
    app.dependency_overrides.pop(get_current_user, None)


# ── OTP /request ────────────────────────────────────────────────────


def test_otp_request_returns_sent(stub_otp_service):
    resp = client.post(
        "/api/v1/mobile/auth/otp/request",
        json={"phoneNumber": "+254712345678"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "sent"
    assert body["expires_in_seconds"] == 300


def test_otp_request_requires_phone():
    resp = client.post("/api/v1/mobile/auth/otp/request", json={})
    assert resp.status_code == 422


# ── OTP /verify ─────────────────────────────────────────────────────


def test_otp_verify_returns_tokens(stub_otp_service, stub_mobile_auth):
    resp = client.post(
        "/api/v1/mobile/auth/otp/verify",
        json={"phoneNumber": "+254712345678", "code": "123456"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["accessToken"] == "fake.access.token"
    assert data["refreshToken"] == "fake.refresh.token"
    assert data["expiresIn"] == 900
    assert "user" in data
    assert data["user"]["phoneNumber"] == "+254712345678"


def test_otp_verify_requires_code(stub_otp_service):
    resp = client.post(
        "/api/v1/mobile/auth/otp/verify",
        json={"phoneNumber": "+254712345678"},
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


# ── /complete-profile ───────────────────────────────────────────────


def test_complete_profile_requires_auth(stub_mobile_auth):
    resp = client.post(
        "/api/v1/mobile/auth/complete-profile",
        json={
            "fullName": "Jane Doe",
            "accountType": "INDIVIDUAL",
        },
    )
    assert resp.status_code == 401, resp.text


def test_complete_profile_returns_user(as_authenticated, stub_mobile_auth):
    resp = client.post(
        "/api/v1/mobile/auth/complete-profile",
        json={
            "fullName": "Jane Doe",
            "accountType": "INDIVIDUAL",
        },
    )
    assert resp.status_code == 200, resp.text
    user = resp.json()["data"]["user"]
    assert user["profileCompleted"] is False
    assert "id" in user
