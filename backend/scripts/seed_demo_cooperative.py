"""Seeds one complete cooperative-operations demo scenario against a
deployed instance that already has a platform ADMINISTRATOR:

- One cooperative
- One cooperative admin (FARMER_COOPERATIVE, cooperative_role=ADMIN)
- Two cooperative members (FARMER_COOPERATIVE, cooperative_role=MEMBER)
- One driver, attached to the cooperative
- One logistics manager and one market analyst, each granted real access
  to the cooperative via cooperative_access_grants (NOT via cooperative_id
  on their own user row — that field is meaningless for these two roles;
  see Multi-Tenancy & Roles in the wiki)
- Five produce lots, logged by the two members, spanning a range of
  harvest ages so storage-risk shows a realistic spread
- Four shipments linked to those produce lots (so tenancy is inherited
  correctly), showing an active operational picture: one already
  DELIVERED, one currently IN_TRANSIT with the driver assigned to it
  right now, and two SCHEDULED for the days ahead

This script does NOT create a platform administrator — it requires one to
already exist (as stated) and fails clearly if it can't find one, rather
than silently creating a surprise admin account on a real deployment.

Passwords: every new account gets its own random TEMPORARY password
(printed once, at the end — this is the only place it's ever shown) and
is left with profile_completed=False. That combination means both of these
work, on purpose:
  - Logging in with email + the temporary password works right away, for
    an immediate demo/walkthrough.
  - Choosing "Email me a sign-in code" instead of the password routes
    them to the app's own "set your password" screen (since
    profile_completed is still false) — the real, already-built
    must-change-password flow, not something this script invents.
Tell every recipient to do the latter before relying on the account for
anything real.

Safe to re-run: an existing user/cooperative/grant is reused as-is (no new
password is generated for an already-existing user); produce and
shipments are skipped entirely if the cooperative already has any produce
logged, so re-running never duplicates data.

Usage (from the running backend container):
    python scripts/seed_demo_cooperative.py
"""

import asyncio
import secrets
import string
import sys
from datetime import datetime, timedelta, timezone

from app.application.cooperative_access_grant_service import CooperativeAccessGrantService
from app.application.produce_service import ProduceService
from app.application.shipment_service import ShipmentService
from app.core.security import hash_password
from app.domain.entities import (
    CommodityClass,
    CooperativeRole,
    ShipmentStatus,
    User,
    UserRole,
)
from app.infrastructure.cooperative_access_grant_repository import SqlAlchemyCooperativeAccessGrantRepository
from app.infrastructure.cooperative_repository import SqlAlchemyCooperativeRepository
from app.infrastructure.db import async_session_factory
from app.infrastructure.produce_repository import SqlAlchemyProduceRepository
from app.infrastructure.shipment_repository import SqlAlchemyShipmentRepository
from app.infrastructure.user_repository import SqlAlchemyUserRepository

COOPERATIVE_NAME = "Meru Highlands Farmer Cooperative"

# (email, full_name, role, cooperative_role)
DEMO_USERS = [
    ("coopadmin@freshsupplies-demo.com", "Grace Wanjiru", UserRole.FARMER_COOPERATIVE, CooperativeRole.ADMIN),
    ("member1@freshsupplies-demo.com", "Peter Mwangi", UserRole.FARMER_COOPERATIVE, CooperativeRole.MEMBER),
    ("member2@freshsupplies-demo.com", "Alice Njeri", UserRole.FARMER_COOPERATIVE, CooperativeRole.MEMBER),
    ("driver@freshsupplies-demo.com", "Samuel Kimani", UserRole.DRIVER, None),
    ("manager@freshsupplies-demo.com", "Beatrice Otieno", UserRole.LOGISTICS_MANAGER, None),
    ("analyst@freshsupplies-demo.com", "Daniel Kiptoo", UserRole.MARKET_ANALYST, None),
]

PRODUCE_LOTS = [
    # (member index into DEMO_USERS, name, variety, qty_kg, price/kg, grade, harvest_days_ago, storage_location)
    (1, "Mangoes", "Apple Mango", 400.0, 140.0, "Grade 1", 1, "Meru Cold Store A"),
    (1, "Avocado", "Hass", 250.0, 180.0, "Grade 1", 3, "Meru Cold Store A"),
    (2, "Bananas", "Kiganda", 300.0, 45.0, "Grade 1", 2, "Meru Cold Store B"),
    (2, "Tomatoes", "Roma", 150.0, 60.0, "Grade 2", 5, "Meru Cold Store B"),
    (1, "French Beans", "Star 2000", 100.0, 220.0, "Grade 1", 0, "Meru Cold Store A"),
]

# (produce index into PRODUCE_LOTS, origin, destination, status, days_from_now)
SHIPMENTS = [
    (0, "Meru Town", "Nairobi Gikomba Market", ShipmentStatus.DELIVERED, -2),
    (1, "Meru Town", "Mombasa Kongowea Market", ShipmentStatus.IN_TRANSIT, 0),
    (2, "Meru Town", "Nakuru Wakulima Market", ShipmentStatus.SCHEDULED, 2),
    (3, "Meru Town", "Kisumu Open Air Market", ShipmentStatus.SCHEDULED, 3),
]

ORIGIN_COORDS = (0.0500, 37.6500)  # Meru
DESTINATION_COORDS = {
    "Nairobi Gikomba Market": (-1.2864, 36.8300),
    "Mombasa Kongowea Market": (-4.0435, 39.6682),
    "Nakuru Wakulima Market": (-0.3031, 36.0800),
    "Kisumu Open Air Market": (-0.0917, 34.7680),
}


def _generate_temp_password() -> str:
    # Satisfies the app's own complexity rule (upper + lower + digit) with
    # margin to spare — see _validate_password_complexity in schemas.py.
    alphabet = string.ascii_letters + string.digits
    while True:
        candidate = "".join(secrets.choice(alphabet) for _ in range(14)) + secrets.choice("!@#$%")
        if (
            any(c.isupper() for c in candidate)
            and any(c.islower() for c in candidate)
            and any(c.isdigit() for c in candidate)
        ):
            return candidate


async def require_existing_admin(users: SqlAlchemyUserRepository) -> User:
    admin = next((u for u in await users.list_all() if u.role == UserRole.ADMINISTRATOR), None)
    if not admin:
        sys.exit(
            "No ADMINISTRATOR account found on this instance. This script deliberately does not "
            "create one — bootstrap a platform admin first, then re-run this script."
        )
    return admin


async def get_or_create_user(
    users: SqlAlchemyUserRepository,
    *,
    email: str,
    full_name: str,
    role: UserRole,
    cooperative_id,
    cooperative_role,
    temp_passwords: dict[str, str],
) -> User:
    existing = await users.get_by_email(email)
    if existing:
        print(f"  reusing existing {role.value}: {email} (no new password generated)")
        return existing
    pending = await users.create_pending(
        email=email,
        full_name=full_name,
        role=role,
        cooperative_id=cooperative_id,
        cooperative_role=cooperative_role,
    )
    temp_password = _generate_temp_password()
    user = await users.update_admin_user(pending.id, hashed_password=hash_password(temp_password))
    temp_passwords[email] = temp_password
    print(f"  created {role.value}: {email}")
    return user


async def seed() -> None:
    temp_passwords: dict[str, str] = {}

    async with async_session_factory() as session:
        users = SqlAlchemyUserRepository(session)
        cooperatives = SqlAlchemyCooperativeRepository(session)
        grants = SqlAlchemyCooperativeAccessGrantRepository(session)
        produce_repo = SqlAlchemyProduceRepository(session)
        shipment_repo = SqlAlchemyShipmentRepository(session)

        admin = await require_existing_admin(users)
        print(f"Using existing administrator: {admin.email}")

        existing_coops = await cooperatives.list_all()
        coop = next((c for c in existing_coops if c.name == COOPERATIVE_NAME), None)
        if coop:
            print(f"Reusing existing cooperative: {coop.name}")
        else:
            coop = await cooperatives.create(name=COOPERATIVE_NAME, created_by=admin.id)
            print(f"Created cooperative: {coop.name}")

        print("Provisioning demo users...")
        created_users: dict[str, User] = {}
        for email, full_name, role, coop_role in DEMO_USERS:
            needs_coop_id = role in (UserRole.FARMER_COOPERATIVE, UserRole.DRIVER)
            user = await get_or_create_user(
                users,
                email=email,
                full_name=full_name,
                role=role,
                cooperative_id=coop.id if needs_coop_id else None,
                cooperative_role=coop_role,
                temp_passwords=temp_passwords,
            )
            created_users[email] = user

        manager = created_users["manager@freshsupplies-demo.com"]
        analyst = created_users["analyst@freshsupplies-demo.com"]
        driver = created_users["driver@freshsupplies-demo.com"]
        members = [created_users["member1@freshsupplies-demo.com"], created_users["member2@freshsupplies-demo.com"]]

        print("Granting cooperative access to staff...")
        grant_service = CooperativeAccessGrantService(grants, users, cooperatives)
        for staff in (manager, analyst):
            already_granted = coop.id in await grants.list_cooperative_ids_for(staff.id)
            if already_granted:
                print(f"  {staff.email} already granted -> {coop.name}")
                continue
            await grant_service.grant(actor=admin, user_id=staff.id, cooperative_id=coop.id)
            print(f"  granted {staff.email} -> {coop.name}")

        existing_produce = await produce_repo.list_all(cooperative_ids=[coop.id])
        if existing_produce:
            print(
                f"Cooperative already has {len(existing_produce)} produce lot(s) — "
                "skipping produce/shipment seeding to avoid duplicates."
            )
        else:
            print("Logging produce...")
            produce_service = ProduceService(produce_repo, grants)
            created_produce = []
            now = datetime.now(timezone.utc)
            for member_idx, name, variety, qty, price, grade, days_ago, location in PRODUCE_LOTS:
                member = members[member_idx - 1]
                item = await produce_service.create_produce(
                    actor=member,
                    name=name,
                    variety=variety,
                    quantity_kg=qty,
                    unit_price=price,
                    quality_grade=grade,
                    harvest_date=now - timedelta(days=days_ago),
                    storage_location=location,
                    commodity_class=CommodityClass.PERISHABLE,
                    storage_temperature_c=4.0,
                    storage_pressure_psi=30.0,
                )
                created_produce.append(item)
                print(f"  {name} ({variety}) — {qty}kg, logged by {member.full_name}")

            print("Creating shipments (active operational picture)...")
            shipment_service = ShipmentService(shipment_repo, grants, users, produce_repo)
            created_shipments = []
            for produce_idx, origin, destination, status, days_from_now in SHIPMENTS:
                produce_item = created_produce[produce_idx]
                dest_lat, dest_lon = DESTINATION_COORDS[destination]
                shipment = await shipment_service.create_shipment(
                    actor=manager,
                    origin=origin,
                    destination=destination,
                    produce_type=produce_item.name,
                    scheduled_date=now + timedelta(days=days_from_now),
                    origin_latitude=ORIGIN_COORDS[0],
                    origin_longitude=ORIGIN_COORDS[1],
                    destination_latitude=dest_lat,
                    destination_longitude=dest_lon,
                    quantity_kg=produce_item.quantity_kg,
                    produce_id=produce_item.id,
                    harvest_date_snapshot=produce_item.harvest_date,
                )
                if status != ShipmentStatus.SCHEDULED:
                    shipment = await shipment_service.update_shipment(
                        shipment.id, actor=manager, status=status,
                        delivery_date=now - timedelta(days=1) if status == ShipmentStatus.DELIVERED else None,
                    )
                created_shipments.append(shipment)
                tag = " <-- ACTIVE, en route right now" if status == ShipmentStatus.IN_TRANSIT else ""
                print(f"  {origin} -> {destination} ({produce_item.name}, {status.value}){tag}")

            in_transit = next((s for s in created_shipments if s.status == ShipmentStatus.IN_TRANSIT), None)
            if in_transit:
                await shipment_service.assign_driver(in_transit.id, actor=manager, driver_user_id=driver.id)
                print(f"  assigned {driver.full_name} to the active in-transit shipment")

    print("\nDone.")
    if temp_passwords:
        print("\nTemporary passwords (shown once — these are NOT stored anywhere else):")
        role_by_email = {email: role for email, _, role, _ in DEMO_USERS}
        for email, password in temp_passwords.items():
            print(f"  {role_by_email[email].value:<18} {email:<35} {password}")
        print(
            "\nEach of these can log in immediately with email + this password, but they should "
            "instead choose \"Email me a sign-in code\" on first login — since these accounts still "
            "have profile_completed=false, that routes them to the app's own \"set your password\" "
            "screen, which is the real must-change-password flow already built into the app."
        )
    else:
        print("No new accounts were created — everything already existed.")


if __name__ == "__main__":
    asyncio.run(seed())
