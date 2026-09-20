"""Top-down account provisioning: admin/cooperative-admin invites, web
email-OTP first login, and the removal of self-registration.

Exercises the service layer directly against fake in-memory repositories (no
DB needed), same style as test_tenancy.py. SMTP_ENABLED is false in tests, so
send_invite_email/send_otp_email just log — no mocking needed.
"""

import asyncio
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.application.admin_service import AdminService
from app.application.admin_tenant_service import AdminTenantService
from app.application.auth_service import AuthService
from app.application.cooperative_member_service import CooperativeMemberService
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.domain.entities import Cooperative, CooperativeRole, User, UserRole

run = asyncio.run


def _user(
    role: UserRole,
    *,
    user_id: UUID | None = None,
    cooperative_id: UUID | None = None,
    cooperative_role: CooperativeRole | None = None,
    profile_completed: bool = True,
    hashed_password: str = "x",
) -> User:
    return User(
        id=user_id or uuid4(),
        email=f"{user_id or uuid4()}@example.com",
        full_name="Test User",
        hashed_password=hashed_password,
        role=role,
        organization_name=None,
        avatar_url=None,
        created_at=datetime.now(timezone.utc),
        phone_number=None,
        account_type=None,
        cooperative_id=cooperative_id,
        phone_verified=True,
        profile_completed=profile_completed,
        cooperative_role=cooperative_role,
    )


class FakeUserRepository:
    def __init__(self, users: list[User] | None = None):
        self._users = {u.id: u for u in (users or [])}

    async def get_by_id(self, user_id):
        return self._users.get(user_id)

    async def get_by_email(self, email):
        return next((u for u in self._users.values() if u.email == email), None)

    async def create_pending(
        self, *, email, full_name, role, organization_name=None, cooperative_id=None, cooperative_role=None
    ):
        user = User(
            id=uuid4(),
            email=email,
            full_name=full_name,
            hashed_password="pending_invite_no_password",
            role=role,
            organization_name=organization_name,
            avatar_url=None,
            created_at=datetime.now(timezone.utc),
            phone_number=None,
            account_type=None,
            cooperative_id=cooperative_id,
            phone_verified=False,
            profile_completed=False,
            cooperative_role=cooperative_role,
        )
        self._users[user.id] = user
        return user

    async def update_admin_user(
        self,
        user_id,
        *,
        full_name=None,
        organization_name=None,
        role=None,
        is_active=None,
        hashed_password=None,
        cooperative_id=None,
        cooperative_role=None,
        profile_completed=None,
    ):
        from dataclasses import replace

        user = self._users.get(user_id)
        if user is None:
            return None
        updated = replace(
            user,
            full_name=full_name if full_name is not None else user.full_name,
            hashed_password=hashed_password if hashed_password is not None else user.hashed_password,
            profile_completed=profile_completed if profile_completed is not None else user.profile_completed,
        )
        self._users[user_id] = updated
        return updated

    async def list_by_cooperative(self, cooperative_id):
        return [u for u in self._users.values() if u.cooperative_id == cooperative_id]


class FakeCooperativeRepository:
    def __init__(self):
        self._coops: dict[UUID, Cooperative] = {}

    async def get_by_id(self, cooperative_id):
        return self._coops.get(cooperative_id)

    async def create(self, *, name, created_by):
        coop = Cooperative(id=uuid4(), name=name, created_by=created_by, created_at=datetime.now(timezone.utc))
        self._coops[coop.id] = coop
        return coop

    async def list_all(self):
        return list(self._coops.values())

    async def update(self, cooperative_id, *, name=None):
        return self._coops.get(cooperative_id)


class FakeUsageRepository:
    async def get_cooperative_usage(self, cooperative_id):
        return {}

    async def list_cooperative_usage(self):
        return []


class FakeOTPService:
    def __init__(self):
        self.requested: list[str] = []
        self.verified: list[tuple[str, str]] = []

    async def request_otp(self, email):
        self.requested.append(email)
        return {"status": "sent", "expires_in_seconds": 300}

    async def verify_otp(self, email, code):
        self.verified.append((email, code))
        return True


# --------------------------------------------------------------- AdminService


def test_admin_create_user_is_passwordless_and_pending():
    users = FakeUserRepository()
    service = AdminService(users, FakeCooperativeRepository())

    user = run(
        service.create_user(
            email="analyst@example.com", full_name="Ana Lyst", role=UserRole.MARKET_ANALYST, organization_name=None
        )
    )

    assert user.profile_completed is False
    assert user.hashed_password == "pending_invite_no_password"


def test_admin_create_user_duplicate_email_conflict():
    existing = _user(UserRole.MARKET_ANALYST)
    users = FakeUserRepository([existing])
    service = AdminService(users, FakeCooperativeRepository())

    with pytest.raises(ConflictError):
        run(
            service.create_user(
                email=existing.email, full_name="Dup", role=UserRole.MARKET_ANALYST, organization_name=None
            )
        )


def test_admin_create_driver_with_cooperative_id():
    users = FakeUserRepository()
    coops = FakeCooperativeRepository()
    coop = run(coops.create(name="Kirinyaga Coop", created_by=uuid4()))
    service = AdminService(users, coops)

    driver = run(
        service.create_user(
            email="driver@example.com",
            full_name="Dan Driver",
            role=UserRole.DRIVER,
            organization_name=None,
            cooperative_id=coop.id,
        )
    )

    assert driver.role == UserRole.DRIVER
    assert driver.cooperative_id == coop.id


def test_admin_create_user_concurrent_duplicate_email_raises_conflict_not_500():
    # The get_by_email check is only advisory — two concurrent invites of
    # the same email can both pass it and race on the real unique
    # constraint, which surfaces here as an IntegrityError from create_pending.
    class RacyUserRepository(FakeUserRepository):
        async def create_pending(self, **kwargs):
            raise IntegrityError("duplicate email", {}, Exception("uq_users_email"))

    service = AdminService(RacyUserRepository(), FakeCooperativeRepository())

    with pytest.raises(ConflictError):
        run(
            service.create_user(
                email="racer@example.com", full_name="Race Condition", role=UserRole.MARKET_ANALYST, organization_name=None
            )
        )


def test_admin_create_user_rejects_unknown_cooperative_id():
    users = FakeUserRepository()
    service = AdminService(users, FakeCooperativeRepository())

    with pytest.raises(NotFoundError):
        run(
            service.create_user(
                email="driver@example.com",
                full_name="Dan Driver",
                role=UserRole.DRIVER,
                organization_name=None,
                cooperative_id=uuid4(),
            )
        )


# ------------------------------------------------------- CooperativeMemberService


def test_cooperative_admin_can_add_member_and_driver():
    coop_id = uuid4()
    admin = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_id, cooperative_role=CooperativeRole.ADMIN)
    users = FakeUserRepository([admin])
    service = CooperativeMemberService(users)

    member = run(service.create_member(actor=admin, email="member@example.com", full_name="M One", role=UserRole.FARMER_COOPERATIVE))
    assert member.cooperative_id == coop_id
    assert member.cooperative_role == CooperativeRole.MEMBER

    driver = run(service.create_member(actor=admin, email="driver@example.com", full_name="D One", role=UserRole.DRIVER))
    assert driver.cooperative_id == coop_id
    assert driver.cooperative_role is None


def test_cooperative_member_cannot_be_added_to_a_different_cooperative():
    # cooperative_id/cooperative_role are never taken from the caller — the
    # service only exposes email/full_name/role, so there is nothing to pass.
    coop_id = uuid4()
    admin = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_id, cooperative_role=CooperativeRole.ADMIN)
    users = FakeUserRepository([admin])
    service = CooperativeMemberService(users)

    member = run(service.create_member(actor=admin, email="m@example.com", full_name="M", role=UserRole.FARMER_COOPERATIVE))
    assert member.cooperative_id == coop_id


def test_plain_member_cannot_add_members():
    coop_id = uuid4()
    plain_member = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_id, cooperative_role=CooperativeRole.MEMBER)
    service = CooperativeMemberService(FakeUserRepository([plain_member]))

    with pytest.raises(ForbiddenError):
        run(service.create_member(actor=plain_member, email="x@example.com", full_name="X", role=UserRole.FARMER_COOPERATIVE))


@pytest.mark.parametrize("role", [UserRole.ADMINISTRATOR, UserRole.LOGISTICS_MANAGER, UserRole.MARKET_ANALYST])
def test_cooperative_admin_cannot_create_staff_or_admin_roles(role):
    coop_id = uuid4()
    admin = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_id, cooperative_role=CooperativeRole.ADMIN)
    service = CooperativeMemberService(FakeUserRepository([admin]))

    with pytest.raises(ValidationError):
        run(service.create_member(actor=admin, email="x@example.com", full_name="X", role=role))


def test_non_cooperative_role_cannot_add_members():
    analyst = _user(UserRole.MARKET_ANALYST)
    service = CooperativeMemberService(FakeUserRepository([analyst]))

    with pytest.raises(ForbiddenError):
        run(service.create_member(actor=analyst, email="x@example.com", full_name="X", role=UserRole.DRIVER))


def test_list_members_scoped_to_own_cooperative():
    coop_a, coop_b = uuid4(), uuid4()
    admin_a = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_a, cooperative_role=CooperativeRole.ADMIN)
    member_a = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_a, cooperative_role=CooperativeRole.MEMBER)
    member_b = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_b, cooperative_role=CooperativeRole.MEMBER)
    service = CooperativeMemberService(FakeUserRepository([admin_a, member_a, member_b]))

    members = run(service.list_members(actor=admin_a))
    assert {m.id for m in members} == {admin_a.id, member_a.id}


# ----------------------------------------------------------- AdminTenantService


def test_create_tenant_with_admin_provisions_cooperative_admin():
    admin = _user(UserRole.ADMINISTRATOR)
    users = FakeUserRepository([admin])
    service = AdminTenantService(FakeCooperativeRepository(), FakeUsageRepository(), users)

    cooperative = run(
        service.create_tenant(
            actor=admin, name="Nyeri Coop", admin_email="coopadmin@example.com", admin_full_name="Coop Admin"
        )
    )

    created = run(users.get_by_email("coopadmin@example.com"))
    assert created is not None
    assert created.cooperative_id == cooperative.id
    assert created.cooperative_role == CooperativeRole.ADMIN
    assert created.profile_completed is False


def test_create_tenant_without_admin_fields_only_creates_cooperative():
    admin = _user(UserRole.ADMINISTRATOR)
    users = FakeUserRepository([admin])
    service = AdminTenantService(FakeCooperativeRepository(), FakeUsageRepository(), users)

    cooperative = run(service.create_tenant(actor=admin, name="Solo Coop"))
    assert cooperative.name == "Solo Coop"


def test_create_tenant_rejects_non_administrator():
    non_admin = _user(UserRole.LOGISTICS_MANAGER)
    service = AdminTenantService(FakeCooperativeRepository(), FakeUsageRepository(), FakeUserRepository([non_admin]))

    with pytest.raises(ForbiddenError):
        run(service.create_tenant(actor=non_admin, name="Nope"))


# --------------------------------------------------------------- AuthService


def test_request_login_otp_rejects_unknown_email():
    service = AuthService(FakeUserRepository())
    with pytest.raises(NotFoundError):
        run(service.request_login_otp("nobody@example.com", FakeOTPService()))


def test_request_login_otp_succeeds_for_known_email():
    user = _user(UserRole.FARMER_COOPERATIVE)
    service = AuthService(FakeUserRepository([user]))
    otp = FakeOTPService()

    result = run(service.request_login_otp(user.email, otp))
    assert result["status"] == "sent"
    assert otp.requested == [user.email]


def test_verify_login_otp_rejects_unknown_email():
    service = AuthService(FakeUserRepository())
    with pytest.raises(NotFoundError):
        run(service.verify_login_otp("nobody@example.com", "123456", FakeOTPService()))


def test_verify_login_otp_issues_tokens_for_known_email():
    user = _user(UserRole.FARMER_COOPERATIVE)
    service = AuthService(FakeUserRepository([user]))

    result_user, access_token, expires_in, refresh_token = run(
        service.verify_login_otp(user.email, "123456", FakeOTPService())
    )
    assert result_user.id == user.id
    assert access_token
    assert refresh_token


def test_set_password_first_time_completes_profile():
    user = _user(UserRole.MARKET_ANALYST, profile_completed=False, hashed_password="pending_invite_no_password")
    service = AuthService(FakeUserRepository([user]))

    updated = run(service.set_password(user.id, "NewPass123"))
    assert updated.profile_completed is True
    assert updated.hashed_password != "pending_invite_no_password"


def test_set_password_rejects_when_already_set():
    user = _user(UserRole.MARKET_ANALYST, profile_completed=True)
    service = AuthService(FakeUserRepository([user]))

    with pytest.raises(ConflictError):
        run(service.set_password(user.id, "NewPass123"))


# --------------------------------------------------------- MobileAuthService


def test_mobile_otp_login_does_not_auto_create_unknown_email():
    from app.application.mobile_auth_service import MobileAuthService

    service = MobileAuthService(FakeUserRepository(), otp_repository=None)
    with pytest.raises(NotFoundError):
        run(service.otp_login("nobody@example.com"))


def test_mobile_otp_login_succeeds_for_provisioned_account():
    from app.application.mobile_auth_service import MobileAuthService

    user = _user(UserRole.DRIVER)
    service = MobileAuthService(FakeUserRepository([user]), otp_repository=None)

    result_user, access_token, expires_in, refresh_token = run(service.otp_login(user.email))
    assert result_user.id == user.id
    assert access_token


# --------------------------------------------------------------- API surface


def test_register_route_removed():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    resp = client.post(
        "/api/v1/auth/register",
        json={"fullName": "X", "email": "x@example.com", "password": "Xxxxxxx1", "role": "FARMER_COOPERATIVE"},
    )
    assert resp.status_code == 404


def test_cooperative_members_route_requires_cooperative_admin():
    from fastapi.testclient import TestClient

    from app.api.deps import get_current_user
    from app.infrastructure.db import get_db_session
    from app.main import app

    client = TestClient(app)
    non_admin = _user(UserRole.FARMER_COOPERATIVE, cooperative_role=CooperativeRole.MEMBER)

    async def _dummy_db():
        yield None

    async def _stub_current_user():
        return non_admin

    app.dependency_overrides[get_db_session] = _dummy_db
    app.dependency_overrides[get_current_user] = _stub_current_user
    try:
        resp = client.post(
            "/api/v1/cooperative/members",
            json={"fullName": "New Member", "email": "new@example.com", "role": "FARMER_COOPERATIVE"},
        )
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.pop(get_db_session, None)
        app.dependency_overrides.pop(get_current_user, None)
