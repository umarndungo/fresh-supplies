"""Multi-tenancy regression tests — shipments, produce, and grants.

Exercises the service layer directly against fake in-memory repositories (no
DB needed). Matches backend/docs/multitenancy_design.md: cooperative members
share visibility, solo farmers are isolated, LOGISTICS_MANAGER/MARKET_ANALYST
see only cooperatives they're explicitly granted (none by default), a
cooperative ADMIN can mutate any member's record while a plain MEMBER can
only mutate their own, and ADMINISTRATOR is refused outright — it manages
tenants/billing, never shipment/produce content.

No pytest-asyncio in this project's test deps, so async service calls are
driven with asyncio.run() from plain sync test functions.
"""

import asyncio
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from sqlalchemy.exc import IntegrityError

from app.application.cooperative_access_grant_service import CooperativeAccessGrantService
from app.application.produce_service import ProduceService
from app.application.shipment_service import ShipmentService
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.domain.entities import (
    CommodityClass,
    Cooperative,
    CooperativeRole,
    OwnerType,
    ProduceItem,
    ProduceStatus,
    Shipment,
    ShipmentStatus,
    User,
    UserRole,
)

run = asyncio.run


def _user(
    role: UserRole,
    *,
    user_id: UUID | None = None,
    cooperative_id: UUID | None = None,
    cooperative_role: CooperativeRole | None = None,
) -> User:
    return User(
        id=user_id or uuid4(),
        email="user@example.com",
        full_name="Test User",
        hashed_password="x",
        role=role,
        organization_name=None,
        avatar_url=None,
        created_at=datetime.now(timezone.utc),
        phone_number=None,
        account_type=None,
        cooperative_id=cooperative_id,
        phone_verified=True,
        profile_completed=True,
        cooperative_role=cooperative_role,
    )


def _shipment(
    *,
    created_by: UUID,
    owner_type: OwnerType,
    cooperative_id: UUID | None = None,
    driver_user_id: UUID | None = None,
) -> Shipment:
    return Shipment(
        id=uuid4(),
        origin="Nakuru",
        destination="Nairobi",
        produce_type="Tomatoes",
        status=ShipmentStatus.SCHEDULED,
        scheduled_date=datetime.now(timezone.utc),
        delivery_date=None,
        created_by=created_by,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        cooperative_id=cooperative_id,
        owner_type=owner_type,
        driver_user_id=driver_user_id,
    )


def _produce(*, created_by: UUID, owner_type: OwnerType, cooperative_id: UUID | None = None) -> ProduceItem:
    return ProduceItem(
        id=uuid4(),
        name="Tomatoes",
        variety="Roma",
        quantity_kg=100.0,
        unit_price=90.0,
        quality_grade="A",
        harvest_date=datetime.now(timezone.utc),
        storage_location="Warehouse 1",
        commodity_class=CommodityClass.PERISHABLE,
        owner_type=owner_type,
        created_by=created_by,
        status=ProduceStatus.AVAILABLE,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        cooperative_id=cooperative_id,
    )


class FakeShipmentRepository:
    def __init__(self, shipments: list[Shipment]):
        self._shipments = {s.id: s for s in shipments}

    async def list_all(self, *, owner_id=None, cooperative_ids=None, driver_user_id=None):
        cooperative_ids = set(cooperative_ids) if cooperative_ids is not None else None
        if owner_id is None and cooperative_ids is None and driver_user_id is None:
            return list(self._shipments.values())
        out = []
        for s in self._shipments.values():
            if driver_user_id is not None and s.driver_user_id == driver_user_id:
                out.append(s)
            elif owner_id is not None and s.owner_type == OwnerType.INDIVIDUAL and s.created_by == owner_id:
                out.append(s)
            elif cooperative_ids and s.owner_type == OwnerType.COOPERATIVE and s.cooperative_id in cooperative_ids:
                out.append(s)
        return out

    async def get_by_id(self, shipment_id):
        return self._shipments.get(shipment_id)

    async def create(self, *, owner_type, cooperative_id=None, created_by, **fields):
        shipment = _shipment(created_by=created_by, owner_type=owner_type, cooperative_id=cooperative_id)
        self._shipments[shipment.id] = shipment
        return shipment

    async def update(self, shipment_id, **fields):
        from dataclasses import replace

        shipment = self._shipments.get(shipment_id)
        if not shipment:
            return None
        updated = replace(shipment, **{k: v for k, v in fields.items() if v is not None})
        self._shipments[shipment_id] = updated
        return updated

    async def delete(self, shipment_id):
        return self._shipments.pop(shipment_id, None) is not None


class FakeProduceRepository:
    def __init__(self, items: list[ProduceItem]):
        self._items = {p.id: p for p in items}

    async def list_all(self, *, owner_id=None, cooperative_ids=None):
        cooperative_ids = set(cooperative_ids) if cooperative_ids is not None else None
        if owner_id is None and cooperative_ids is None:
            return list(self._items.values())
        out = []
        for p in self._items.values():
            if owner_id is not None and p.owner_type == OwnerType.INDIVIDUAL and p.created_by == owner_id:
                out.append(p)
            elif cooperative_ids and p.owner_type == OwnerType.COOPERATIVE and p.cooperative_id in cooperative_ids:
                out.append(p)
        return out

    async def get_by_id(self, produce_id):
        return self._items.get(produce_id)

    async def update(self, produce_id, **fields):
        return self._items.get(produce_id)

    async def delete(self, produce_id):
        return self._items.pop(produce_id, None) is not None


class FakeGrantsRepository:
    def __init__(self, grants: dict[UUID, set[UUID]] | None = None):
        self._grants = grants or {}  # user_id -> {cooperative_id, ...}

    async def list_cooperative_ids_for(self, user_id):
        return list(self._grants.get(user_id, set()))

    async def create(self, *, user_id, cooperative_id, granted_by):
        # Mirrors the real uq_cooperative_access_grants_user_coop constraint.
        existing = self._grants.setdefault(user_id, set())
        if cooperative_id in existing:
            raise IntegrityError("duplicate grant", {}, Exception("uq_cooperative_access_grants_user_coop"))
        existing.add(cooperative_id)
        return None

    async def delete(self, grant_id):
        return False

    async def list_for_cooperative(self, cooperative_id):
        return []


class FakeUserRepository:
    def __init__(self, users: list[User] | None = None):
        self._users = {u.id: u for u in (users or [])}

    async def get_by_id(self, user_id):
        return self._users.get(user_id)


# --------------------------------------------------------------- shipments


def test_shipment_solo_farmers_are_isolated():
    farmer_a, farmer_b = _user(UserRole.FARMER_COOPERATIVE), _user(UserRole.FARMER_COOPERATIVE)
    shipment_a = _shipment(created_by=farmer_a.id, owner_type=OwnerType.INDIVIDUAL)
    shipment_b = _shipment(created_by=farmer_b.id, owner_type=OwnerType.INDIVIDUAL)
    service = ShipmentService(FakeShipmentRepository([shipment_a, shipment_b]), FakeGrantsRepository(), FakeUserRepository(), FakeProduceRepository([]))

    result = run(service.list_shipments(actor=farmer_a))
    assert {s.id for s in result} == {shipment_a.id}

    with pytest.raises(NotFoundError):
        run(service.get_shipment(shipment_b.id, actor=farmer_a))


def test_shipment_cooperative_members_share_visibility():
    coop_id = uuid4()
    member_1 = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_id, cooperative_role=CooperativeRole.MEMBER)
    member_2 = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_id, cooperative_role=CooperativeRole.MEMBER)
    shipment = _shipment(created_by=member_1.id, owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id)
    service = ShipmentService(FakeShipmentRepository([shipment]), FakeGrantsRepository(), FakeUserRepository(), FakeProduceRepository([]))

    result = run(service.get_shipment(shipment.id, actor=member_2))
    assert result.id == shipment.id


def test_shipment_different_cooperatives_are_isolated():
    coop_a, coop_b = uuid4(), uuid4()
    member_a = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_a)
    member_b = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_b)
    shipment_a = _shipment(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_a)
    service = ShipmentService(FakeShipmentRepository([shipment_a]), FakeGrantsRepository(), FakeUserRepository(), FakeProduceRepository([]))

    with pytest.raises(NotFoundError):
        run(service.get_shipment(shipment_a.id, actor=member_b))
    assert run(service.list_shipments(actor=member_b)) == []
    assert [s.id for s in run(service.list_shipments(actor=member_a))] == [shipment_a.id]


@pytest.mark.parametrize("role", [UserRole.LOGISTICS_MANAGER, UserRole.MARKET_ANALYST])
def test_shipment_staff_without_grants_sees_nothing(role):
    coop_id = uuid4()
    shipment = _shipment(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id)
    service = ShipmentService(FakeShipmentRepository([shipment]), FakeGrantsRepository(), FakeUserRepository(), FakeProduceRepository([]))
    actor = _user(role)

    assert run(service.list_shipments(actor=actor)) == []
    with pytest.raises(NotFoundError):
        run(service.get_shipment(shipment.id, actor=actor))


def test_shipment_logistics_manager_scoped_to_granted_cooperative():
    coop_a, coop_b = uuid4(), uuid4()
    manager = _user(UserRole.LOGISTICS_MANAGER)
    grants = FakeGrantsRepository({manager.id: {coop_a}})
    shipment_a = _shipment(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_a)
    shipment_b = _shipment(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_b)
    service = ShipmentService(FakeShipmentRepository([shipment_a, shipment_b]), grants, FakeUserRepository(), FakeProduceRepository([]))

    result = run(service.list_shipments(actor=manager))
    assert {s.id for s in result} == {shipment_a.id}

    # Can update within the granted cooperative...
    updated = run(service.update_shipment(shipment_a.id, actor=manager, status=ShipmentStatus.IN_TRANSIT))
    assert updated is not None
    # ...but not outside it.
    with pytest.raises(NotFoundError):
        run(service.update_shipment(shipment_b.id, actor=manager, status=ShipmentStatus.IN_TRANSIT))


def test_shipment_market_analyst_cannot_mutate_even_when_granted():
    coop_id = uuid4()
    analyst = _user(UserRole.MARKET_ANALYST)
    grants = FakeGrantsRepository({analyst.id: {coop_id}})
    shipment = _shipment(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id)
    service = ShipmentService(FakeShipmentRepository([shipment]), grants, FakeUserRepository(), FakeProduceRepository([]))

    # Read works...
    assert run(service.get_shipment(shipment.id, actor=analyst)).id == shipment.id
    # ...write does not (MARKET_ANALYST is not in _MANAGE_ROLES at all).
    with pytest.raises(ForbiddenError):
        run(service.update_shipment(shipment.id, actor=analyst, status=ShipmentStatus.IN_TRANSIT))


def test_create_shipment_inherits_tenancy_from_linked_produce():
    # Regression: LOGISTICS_MANAGER (the only role allowed to create
    # shipments) has no personal account_type/cooperative_id — deriving
    # owner_type from the actor used to mint a shipment nobody, including
    # the creating manager, could ever see again. It must come from the
    # produce lot being shipped instead.
    coop_id = uuid4()
    manager = _user(UserRole.LOGISTICS_MANAGER)
    grants = FakeGrantsRepository({manager.id: {coop_id}})
    produce = _produce(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id)
    service = ShipmentService(
        FakeShipmentRepository([]), grants, FakeUserRepository(), FakeProduceRepository([produce])
    )

    shipment = run(
        service.create_shipment(
            actor=manager,
            origin="Kianyaga",
            destination="Nairobi",
            produce_type="Tomatoes",
            scheduled_date=datetime.now(timezone.utc),
            produce_id=produce.id,
        )
    )

    assert shipment.owner_type == OwnerType.COOPERATIVE
    assert shipment.cooperative_id == coop_id
    # And the manager (or any staff granted that cooperative) can now
    # actually see the shipment they just created.
    assert shipment.id in {s.id for s in run(service.list_shipments(actor=manager))}


def test_create_shipment_rejects_produce_outside_manager_grant():
    coop_id = uuid4()
    manager = _user(UserRole.LOGISTICS_MANAGER)  # no grants at all
    produce = _produce(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id)
    service = ShipmentService(
        FakeShipmentRepository([]), FakeGrantsRepository(), FakeUserRepository(), FakeProduceRepository([produce])
    )

    with pytest.raises(NotFoundError):
        run(
            service.create_shipment(
                actor=manager,
                origin="Kianyaga",
                destination="Nairobi",
                produce_type="Tomatoes",
                scheduled_date=datetime.now(timezone.utc),
                produce_id=produce.id,
            )
        )


def test_shipment_administrator_is_refused_entirely():
    admin = _user(UserRole.ADMINISTRATOR)
    shipment = _shipment(created_by=uuid4(), owner_type=OwnerType.INDIVIDUAL)
    service = ShipmentService(FakeShipmentRepository([shipment]), FakeGrantsRepository(), FakeUserRepository(), FakeProduceRepository([]))

    with pytest.raises(ForbiddenError):
        run(service.list_shipments(actor=admin))
    with pytest.raises(ForbiddenError):
        run(service.get_shipment(shipment.id, actor=admin))
    with pytest.raises(ForbiddenError):
        run(service.update_shipment(shipment.id, actor=admin, status=ShipmentStatus.IN_TRANSIT))
    with pytest.raises(ForbiddenError):
        run(service.delete_shipment(shipment.id, actor=admin))


# ------------------------------------------------------- driver assignment


def test_driver_sees_only_assigned_shipments():
    driver = _user(UserRole.DRIVER)
    coop_id = uuid4()
    assigned = _shipment(
        created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id, driver_user_id=driver.id
    )
    not_assigned = _shipment(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id)
    service = ShipmentService(
        FakeShipmentRepository([assigned, not_assigned]), FakeGrantsRepository(), FakeUserRepository(), FakeProduceRepository([])
    )

    result = run(service.list_shipments(actor=driver))
    assert {s.id for s in result} == {assigned.id}
    with pytest.raises(NotFoundError):
        run(service.get_shipment(not_assigned.id, actor=driver))


def test_assign_driver_succeeds_within_granted_cooperative():
    coop_id = uuid4()
    manager = _user(UserRole.LOGISTICS_MANAGER)
    driver = _user(UserRole.DRIVER, cooperative_id=coop_id)
    shipment = _shipment(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id)
    service = ShipmentService(
        FakeShipmentRepository([shipment]),
        FakeGrantsRepository({manager.id: {coop_id}}),
        FakeUserRepository([driver]),
        FakeProduceRepository([]),
    )

    result = run(service.assign_driver(shipment.id, actor=manager, driver_user_id=driver.id))
    assert result.driver_user_id == driver.id


def test_assign_driver_rejects_non_driver_account():
    coop_id = uuid4()
    manager = _user(UserRole.LOGISTICS_MANAGER)
    not_a_driver = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_id)
    shipment = _shipment(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id)
    service = ShipmentService(
        FakeShipmentRepository([shipment]),
        FakeGrantsRepository({manager.id: {coop_id}}),
        FakeUserRepository([not_a_driver]),
        FakeProduceRepository([]),
    )

    with pytest.raises(ValidationError):
        run(service.assign_driver(shipment.id, actor=manager, driver_user_id=not_a_driver.id))


def test_assign_driver_rejects_mismatched_cooperative():
    coop_a, coop_b = uuid4(), uuid4()
    manager = _user(UserRole.LOGISTICS_MANAGER)
    driver_from_coop_b = _user(UserRole.DRIVER, cooperative_id=coop_b)
    shipment = _shipment(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_a)
    service = ShipmentService(
        FakeShipmentRepository([shipment]),
        FakeGrantsRepository({manager.id: {coop_a}}),
        FakeUserRepository([driver_from_coop_b]),
        FakeProduceRepository([]),
    )

    with pytest.raises(ValidationError):
        run(service.assign_driver(shipment.id, actor=manager, driver_user_id=driver_from_coop_b.id))


def test_assign_driver_requires_manager_scope_over_shipment():
    coop_a, coop_b = uuid4(), uuid4()
    manager = _user(UserRole.LOGISTICS_MANAGER)  # granted coop_a, not coop_b
    driver = _user(UserRole.DRIVER, cooperative_id=coop_b)
    shipment = _shipment(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_b)
    service = ShipmentService(
        FakeShipmentRepository([shipment]),
        FakeGrantsRepository({manager.id: {coop_a}}),
        FakeUserRepository([driver]),
        FakeProduceRepository([]),
    )

    with pytest.raises(NotFoundError):
        run(service.assign_driver(shipment.id, actor=manager, driver_user_id=driver.id))


# ----------------------------------------------------------------- produce


def test_produce_cooperative_admin_can_mutate_any_members_item():
    coop_id = uuid4()
    admin_member = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_id, cooperative_role=CooperativeRole.ADMIN)
    plain_member = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_id, cooperative_role=CooperativeRole.MEMBER)
    produce = _produce(created_by=plain_member.id, owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id)
    service = ProduceService(FakeProduceRepository([produce]), FakeGrantsRepository())

    result = run(service.update_produce(produce.id, actor=admin_member, name="Updated by coop admin"))
    assert result is not None


def test_produce_plain_member_cannot_mutate_others_item():
    coop_id = uuid4()
    member_1 = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_id, cooperative_role=CooperativeRole.MEMBER)
    member_2 = _user(UserRole.FARMER_COOPERATIVE, cooperative_id=coop_id, cooperative_role=CooperativeRole.MEMBER)
    produce = _produce(created_by=member_1.id, owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_id)
    service = ProduceService(FakeProduceRepository([produce]), FakeGrantsRepository())

    with pytest.raises(NotFoundError):
        run(service.update_produce(produce.id, actor=member_2, name="Hijacked"))
    with pytest.raises(NotFoundError):
        run(service.delete_produce(produce.id, actor=member_2))


def test_produce_administrator_is_refused_entirely():
    admin = _user(UserRole.ADMINISTRATOR)
    produce = _produce(created_by=uuid4(), owner_type=OwnerType.INDIVIDUAL)
    service = ProduceService(FakeProduceRepository([produce]), FakeGrantsRepository())

    with pytest.raises(ForbiddenError):
        run(service.list_produce(actor=admin))
    with pytest.raises(ForbiddenError):
        run(service.get_produce(produce.id, actor=admin))


@pytest.mark.parametrize("role", [UserRole.LOGISTICS_MANAGER, UserRole.MARKET_ANALYST])
def test_produce_staff_scoped_to_granted_cooperative_only(role):
    coop_a, coop_b = uuid4(), uuid4()
    actor = _user(role)
    grants = FakeGrantsRepository({actor.id: {coop_a}})
    produce_a = _produce(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_a)
    produce_b = _produce(created_by=uuid4(), owner_type=OwnerType.COOPERATIVE, cooperative_id=coop_b)
    service = ProduceService(FakeProduceRepository([produce_a, produce_b]), grants)

    result = run(service.list_produce(actor=actor))
    assert {p.id for p in result} == {produce_a.id}


# ------------------------------------------------------------------ grants


class FakeCooperativeRepository:
    def __init__(self, cooperatives: list[Cooperative]):
        self._cooperatives = {c.id: c for c in cooperatives}

    async def get_by_id(self, cooperative_id):
        return self._cooperatives.get(cooperative_id)

    async def create(self, *, name, created_by):
        raise NotImplementedError

    async def list_all(self):
        return list(self._cooperatives.values())

    async def update(self, cooperative_id, *, name=None):
        return self._cooperatives.get(cooperative_id)


def _cooperative() -> Cooperative:
    return Cooperative(id=uuid4(), name="Test Coop", created_by=uuid4(), created_at=datetime.now(timezone.utc))


def test_grant_rejects_administrator_as_grantee():
    admin_target = _user(UserRole.ADMINISTRATOR)
    granting_admin = _user(UserRole.ADMINISTRATOR)
    coop = _cooperative()
    service = CooperativeAccessGrantService(
        FakeGrantsRepository(), FakeUserRepository([admin_target]), FakeCooperativeRepository([coop])
    )

    with pytest.raises(ValidationError):
        run(service.grant(actor=granting_admin, user_id=admin_target.id, cooperative_id=coop.id))


def test_grant_accepts_logistics_manager_as_grantee():
    target = _user(UserRole.LOGISTICS_MANAGER)
    granting_admin = _user(UserRole.ADMINISTRATOR)
    coop = _cooperative()
    service = CooperativeAccessGrantService(
        FakeGrantsRepository(), FakeUserRepository([target]), FakeCooperativeRepository([coop])
    )

    grant = run(service.grant(actor=granting_admin, user_id=target.id, cooperative_id=coop.id))
    assert grant is None  # FakeGrantsRepository.create() doesn't build an entity; call succeeding is the assertion


def test_grant_duplicate_raises_conflict_not_500():
    # Regression: re-granting a user access they already have hit the DB's
    # uq_cooperative_access_grants_user_coop unique constraint and crashed
    # into an unhandled IntegrityError (500) instead of a clean 409.
    target = _user(UserRole.LOGISTICS_MANAGER)
    granting_admin = _user(UserRole.ADMINISTRATOR)
    coop = _cooperative()
    grants_repo = FakeGrantsRepository({target.id: {coop.id}})
    service = CooperativeAccessGrantService(
        grants_repo, FakeUserRepository([target]), FakeCooperativeRepository([coop])
    )

    with pytest.raises(ConflictError):
        run(service.grant(actor=granting_admin, user_id=target.id, cooperative_id=coop.id))


def test_grant_requires_administrator_actor():
    target = _user(UserRole.LOGISTICS_MANAGER)
    non_admin_actor = _user(UserRole.FARMER_COOPERATIVE)
    coop = _cooperative()
    service = CooperativeAccessGrantService(
        FakeGrantsRepository(), FakeUserRepository([target]), FakeCooperativeRepository([coop])
    )

    with pytest.raises(ForbiddenError):
        run(service.grant(actor=non_admin_actor, user_id=target.id, cooperative_id=coop.id))
