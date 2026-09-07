"""API endpoint tests for the admin user-management routes.

These use a stubbed AdminService so no database is required. They assert the
security boundary (ADMINISTRATOR only), the response envelope, and the
invite/update/deactivate/delete lifecycle.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import ConflictError
from app.domain.entities import User, UserRole
from app.api.deps import get_admin_service, get_current_user
from app.main import app

client = TestClient(app)


def _user(role: UserRole, *, is_active: bool = True) -> User:
    return User(
        id=uuid4(),
        email="admin@example.com",
        full_name="Root Admin",
        hashed_password="x",
        role=role,
        organization_name="Fresh Supplies",
        avatar_url=None,
        created_at=datetime.now(timezone.utc),
        phone_number=None,
        account_type=None,
        cooperative_id=None,
        phone_verified=False,
        profile_completed=True,
        is_active=is_active,
    )


@pytest.fixture()
def admin_user() -> User:
    return _user(UserRole.ADMINISTRATOR)


class StubAdminService:
    def __init__(self, actor: User):
        self._actor = actor
        self._users: dict = {}
        self.deleted = []
        self.updated = []

    async def list_users(self):
        return list(self._users.values())

    async def create_user(self, *, email, password, full_name, role, organization_name):
        if any(u.email == email for u in self._users.values()):
            raise ConflictError("An account with this email already exists.", field="email")
        user = _user(role)
        self._users[user.id] = User(
            id=user.id,
            email=email,
            full_name=full_name,
            hashed_password=password,
            role=role,
            organization_name=organization_name,
            avatar_url=None,
            created_at=datetime.now(timezone.utc),
            phone_number=None,
            account_type=None,
            cooperative_id=None,
            phone_verified=False,
            profile_completed=True,
            is_active=True,
        )
        return self._users[user.id]

    async def update_user(self, user_id, *, full_name=None, organization_name=None, role=None, is_active=None, reset_password=None):
        from app.core.exceptions import NotFoundError

        if user_id not in self._users:
            raise NotFoundError("User not found.")
        user = self._users[user_id]
        from dataclasses import replace

        self._users[user_id] = replace(
            user,
            full_name=full_name or user.full_name,
            organization_name=organization_name if organization_name is not None else user.organization_name,
            role=role or user.role,
            is_active=user.is_active if is_active is None else is_active,
        )
        return self._users[user_id]

    async def delete_user(self, user_id, *, actor_id):
        if user_id == actor_id:
            raise ConflictError("You cannot delete your own account.")
        self.deleted.append(user_id)
        self._users.pop(user_id, None)


@pytest.fixture()
def as_admin(admin_user):
    stub = StubAdminService(admin_user)

    async def _stub_current_user():
        return admin_user

    def _stub_service():
        return stub

    app.dependency_overrides[get_current_user] = _stub_current_user
    app.dependency_overrides[get_admin_service] = _stub_service
    yield stub
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_admin_service, None)


def test_admin_users_requires_administrator():
    async def _stub_non_admin():
        return _user(UserRole.MARKET_ANALYST)

    def _stub_service():
        return StubAdminService(_user(UserRole.MARKET_ANALYST))

    app.dependency_overrides[get_current_user] = _stub_non_admin
    app.dependency_overrides[get_admin_service] = _stub_service
    try:
        resp = client.get("/api/v1/admin/users")
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_admin_service, None)
    assert resp.status_code == 403
    assert resp.json()["message"] == "You do not have permission to perform this action."


def test_list_users_envelope(as_admin):
    resp = client.get("/api/v1/admin/users")
    assert resp.status_code == 200
    assert "data" in resp.json() and isinstance(resp.json()["data"], list)


def test_create_user(as_admin):
    resp = client.post(
        "/api/v1/admin/users",
        json={
            "fullName": "Grace Gathoni",
            "email": "grace@example.com",
            "password": "Grace123!",
            "role": "MARKET_ANALYST",
            "organizationName": "Nyeri Coop",
        },
    )
    assert resp.status_code == 201
    body = resp.json()["data"]
    assert body["email"] == "grace@example.com"
    assert body["fullName"] == "Grace Gathoni"
    assert body["role"] == "MARKET_ANALYST"
    assert body["isActive"] is True


def test_create_user_duplicate_email_conflict(as_admin):
    resp = client.post(
        "/api/v1/admin/users",
        json={
            "fullName": "Grace Gathoni",
            "email": "grace@example.com",
            "password": "Grace123!",
            "role": "MARKET_ANALYST",
        },
    )
    assert resp.status_code == 201
    resp = client.post(
        "/api/v1/admin/users",
        json={
            "fullName": "Grace Gathoni",
            "email": "grace@example.com",
            "password": "Grace123!",
            "role": "MARKET_ANALYST",
        },
    )
    assert resp.status_code == 409
    assert "email" in str(resp.json()["errors"])


def test_update_user_deactivate_and_reactivate(as_admin, admin_user):
    created = client.post(
        "/api/v1/admin/users",
        json={
            "fullName": "Paul Mwangi",
            "email": "paul@example.com",
            "password": "Paul123!",
            "role": "FARMER_COOPERATIVE",
        },
    ).json()["data"]
    uid = created["id"]

    resp = client.patch(f"/api/v1/admin/users/{uid}", json={"isActive": False, "role": "LOGISTICS_MANAGER"})
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["isActive"] is False
    assert body["role"] == "LOGISTICS_MANAGER"

    resp = client.patch(f"/api/v1/admin/users/{uid}", json={"isActive": True})
    assert resp.status_code == 200
    assert resp.json()["data"]["isActive"] is True


def test_delete_user(as_admin, admin_user):
    created = client.post(
        "/api/v1/admin/users",
        json={
            "fullName": "Ann Wanjiru",
            "email": "ann@example.com",
            "password": "Ann1234!",
            "role": "MARKET_ANALYST",
        },
    ).json()["data"]
    resp = client.delete(f"/api/v1/admin/users/{created['id']}")
    assert resp.status_code == 204


def test_cannot_delete_own_account(as_admin, admin_user):
    resp = client.delete(f"/api/v1/admin/users/{admin_user.id}")
    assert resp.status_code == 409
    assert "own account" in resp.json()["message"]