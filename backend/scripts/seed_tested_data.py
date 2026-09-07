import asyncio
from datetime import datetime, timezone, timedelta
import random
import uuid

from sqlalchemy import select
from app.infrastructure.db import async_session_factory
from app.infrastructure.models import (
    UserModel,
    ShipmentModel,
    ProduceModel,
    CooperativeModel,
)
from app.domain.entities import (
    ShipmentStatus,
    ProduceStatus,
    CommodityClass,
    UserRole,
)
from app.application.ml_service import predict_spoilage

ORIGINS = [
    {"name": "Eldoret Central Hub", "lat": 0.5143, "lon": 35.2698},
    {"name": "Nakuru Wakulima Hub", "lat": -0.3031, "lon": 36.0800},
    {"name": "Meru Horticultural Center", "lat": 0.0500, "lon": 37.6500},
    {"name": "Naivasha Farm Cluster", "lat": -0.7172, "lon": 36.4312},
    {"name": "Bomet Agribusiness Coop", "lat": -0.7800, "lon": 35.3400},
    {"name": "Machakos Cold Storage", "lat": -1.5177, "lon": 37.2634},
    {"name": "Kisii Banana Processing Hub", "lat": -0.6817, "lon": 34.7667},
    {"name": "Kiambu Green Farms", "lat": -1.1714, "lon": 36.8356},
    {"name": "Nyeri Highlands Depot", "lat": -0.4167, "lon": 36.9500},
]

DESTINATIONS = [
    {"name": "Nairobi Gikomba Market", "lat": -1.2864, "lon": 36.8300},
    {"name": "Mombasa Kongowea Market", "lat": -4.0435, "lon": 39.6682},
    {"name": "Nakuru Wakulima Market", "lat": -0.3031, "lon": 36.0800},
    {"name": "Kisumu Open Air Market", "lat": -0.0917, "lon": 34.7680},
    {"name": "Eldoret Market", "lat": 0.5143, "lon": 35.2698},
    {"name": "Thika Market", "lat": -1.0333, "lon": 37.0693},
    {"name": "Naivasha Market", "lat": -0.7172, "lon": 36.4312},
]

async def seed():
    async with async_session_factory() as session:
        stmt = select(UserModel).order_by(UserModel.created_at.asc())
        users = (await session.execute(stmt)).scalars().all()

        if not users:
            print("ERROR: No users found. Please register a user first.")
            return

        admin_user = next((u for u in users if u.role == UserRole.ADMINISTRATOR), users[0])
        coop_user = next((u for u in users if u.role == UserRole.FARMER_COOPERATIVE), users[-1])

        print(f"Targeting Admin User: {admin_user.full_name} ({admin_user.email})")
        print(f"Targeting Cooperative User: {coop_user.full_name} ({coop_user.email})")

        coop_stmt = select(CooperativeModel).limit(1)
        coop = (await session.execute(coop_stmt)).scalars().first()
        if not coop:
            coop = CooperativeModel(
                id=uuid.uuid4(),
                name="Rift Valley Horticultural Farmers Cooperative",
                created_by=admin_user.id,
                created_at=datetime.now(timezone.utc) - timedelta(days=60),
            )
            session.add(coop)
            await session.flush()
            print(f"Created cooperative: {coop.name}")

        existing_shipments = (await session.execute(select(ShipmentModel))).scalars().all()
        if existing_shipments:
            print(f"Found {len(existing_shipments)} existing shipments. Replacing with tested dataset...")
            for s in existing_shipments:
                await session.delete(s)

        existing_produce = (await session.execute(select(ProduceModel))).scalars().all()
        if existing_produce:
            print(f"Found {len(existing_produce)} existing produce items. Replacing with tested dataset...")
            for p in existing_produce:
                await session.delete(p)

        await session.flush()

        now = datetime.now(timezone.utc)

        shipment_scenarios = [
            # High Risk / Warm ambient long hauls
            {"crop": "Tomatoes", "origin": 0, "dest": 1, "temp": 28.5, "dur": 14.0, "qty": 3500, "status": ShipmentStatus.IN_TRANSIT, "days_ago": 0},
            {"crop": "Mangoes", "origin": 2, "dest": 1, "temp": 29.0, "dur": 12.5, "qty": 4200, "status": ShipmentStatus.IN_TRANSIT, "days_ago": 0},
            {"crop": "Bananas", "origin": 6, "dest": 0, "temp": 26.5, "dur": 9.0, "qty": 5000, "status": ShipmentStatus.IN_TRANSIT, "days_ago": 1},
            {"crop": "Kale", "origin": 7, "dest": 1, "temp": 27.0, "dur": 11.0, "qty": 1800, "status": ShipmentStatus.IN_TRANSIT, "days_ago": 0},
            {"crop": "Tomatoes", "origin": 3, "dest": 0, "temp": 24.5, "dur": 4.5, "qty": 2800, "status": ShipmentStatus.IN_TRANSIT, "days_ago": 0},

            # Moderate Risk / At-Risk
            {"crop": "Avocados", "origin": 8, "dest": 0, "temp": 21.0, "dur": 5.0, "qty": 3800, "status": ShipmentStatus.IN_TRANSIT, "days_ago": 1},
            {"crop": "Tomatoes", "origin": 1, "dest": 0, "temp": 23.0, "dur": 5.5, "qty": 4500, "status": ShipmentStatus.SCHEDULED, "days_ago": -1},
            {"crop": "Bananas", "origin": 6, "dest": 2, "temp": 24.0, "dur": 6.0, "qty": 3200, "status": ShipmentStatus.SCHEDULED, "days_ago": -2},
            {"crop": "Cabbages", "origin": 4, "dest": 0, "temp": 22.5, "dur": 7.0, "qty": 6500, "status": ShipmentStatus.SCHEDULED, "days_ago": -1},
            {"crop": "Mangoes", "origin": 5, "dest": 0, "temp": 24.0, "dur": 3.5, "qty": 2200, "status": ShipmentStatus.SCHEDULED, "days_ago": -2},

            # Low Risk / Cold-Chain Fresh
            {"crop": "Avocados", "origin": 2, "dest": 0, "temp": 14.5, "dur": 6.0, "qty": 4000, "status": ShipmentStatus.IN_TRANSIT, "days_ago": 0},
            {"crop": "Potatoes", "origin": 8, "dest": 0, "temp": 16.0, "dur": 4.5, "qty": 8500, "status": ShipmentStatus.IN_TRANSIT, "days_ago": 0},
            {"crop": "Onions", "origin": 7, "dest": 5, "temp": 18.0, "dur": 2.5, "qty": 5500, "status": ShipmentStatus.SCHEDULED, "days_ago": -1},
            {"crop": "Potatoes", "origin": 1, "dest": 0, "temp": 17.5, "dur": 5.0, "qty": 7000, "status": ShipmentStatus.SCHEDULED, "days_ago": -2},
            {"crop": "Avocados", "origin": 3, "dest": 0, "temp": 15.0, "dur": 3.5, "qty": 3400, "status": ShipmentStatus.SCHEDULED, "days_ago": -1},

            # Completed Deliveries
            {"crop": "Tomatoes", "origin": 3, "dest": 0, "temp": 22.0, "dur": 4.0, "qty": 3000, "status": ShipmentStatus.DELIVERED, "days_ago": 3},
            {"crop": "Bananas", "origin": 6, "dest": 3, "temp": 23.5, "dur": 4.5, "qty": 4100, "status": ShipmentStatus.DELIVERED, "days_ago": 4},
            {"crop": "Avocados", "origin": 2, "dest": 1, "temp": 15.5, "dur": 13.0, "qty": 4500, "status": ShipmentStatus.DELIVERED, "days_ago": 5},
            {"crop": "Mangoes", "origin": 5, "dest": 0, "temp": 22.0, "dur": 3.0, "qty": 2800, "status": ShipmentStatus.DELIVERED, "days_ago": 6},
            {"crop": "Potatoes", "origin": 1, "dest": 3, "temp": 17.0, "dur": 6.5, "qty": 9000, "status": ShipmentStatus.DELIVERED, "days_ago": 7},
            {"crop": "Cabbages", "origin": 4, "dest": 0, "temp": 20.0, "dur": 6.0, "qty": 5800, "status": ShipmentStatus.DELIVERED, "days_ago": 8},
            {"crop": "Onions", "origin": 7, "dest": 0, "temp": 19.0, "dur": 2.0, "qty": 4200, "status": ShipmentStatus.DELIVERED, "days_ago": 10},
            {"crop": "Tomatoes", "origin": 0, "dest": 4, "temp": 21.0, "dur": 2.0, "qty": 2600, "status": ShipmentStatus.DELIVERED, "days_ago": 12},
            {"crop": "Kale", "origin": 7, "dest": 0, "temp": 20.5, "dur": 2.0, "qty": 1500, "status": ShipmentStatus.DELIVERED, "days_ago": 14},
        ]

        shipment_objects = []
        for s in shipment_scenarios:
            origin_node = ORIGINS[s["origin"]]
            dest_node = DESTINATIONS[s["dest"]]

            ml_input = {
                "crop_type": s["crop"],
                "latitude": origin_node["lat"],
                "longitude": origin_node["lon"],
                "Temperature_C": s["temp"],
                "Transit_Duration_Hr": s["dur"],
                "Pressure_PSI": 30.0,
                "baseline_loss_pct": 10.0,
                "quantity_kg": s["qty"],
                "Distance_To_Market_Km": s["dur"] * 45.0,
            }
            try:
                ml_res = predict_spoilage(ml_input)
                spoil_prob = ml_res["spoilage_probability"]
                risk_tier = ml_res["risk_tier"]
                spoil_pred = ml_res["spoil_prediction"]
            except Exception:
                spoil_prob = 0.15
                risk_tier = "FRESH"
                spoil_pred = False

            sched_time = now - timedelta(days=s["days_ago"], hours=random.randint(1, 8))
            deliv_time = (sched_time + timedelta(hours=s["dur"] + 2)) if s["status"] == ShipmentStatus.DELIVERED else None

            shipment = ShipmentModel(
                id=uuid.uuid4(),
                origin=origin_node["name"],
                destination=dest_node["name"],
                produce_type=s["crop"],
                status=s["status"],
                scheduled_date=sched_time,
                delivery_date=deliv_time,
                created_by=admin_user.id,
                cooperative_id=coop.id,
                origin_latitude=origin_node["lat"],
                origin_longitude=origin_node["lon"],
                destination_latitude=dest_node["lat"],
                destination_longitude=dest_node["lon"],
                temperature_c=s["temp"],
                transit_duration_hr=s["dur"],
                pressure_psi=30.0,
                baseline_loss_pct=10.0,
                quantity_kg=float(s["qty"]),
                spoilage_probability=spoil_prob,
                risk_tier=risk_tier,
                spoil_prediction=spoil_pred,
                created_at=sched_time,
                updated_at=sched_time,
            )
            session.add(shipment)
            shipment_objects.append(shipment)

        print(f"Created {len(shipment_objects)} verified shipments with ML predictions.")

        produce_items = [
            {"name": "Tomatoes", "variety": "Roma Grade A", "qty": 4200, "price": 95.0, "grade": "Grade 1", "loc": "Naivasha Cold Room 2", "class": CommodityClass.PERISHABLE, "status": ProduceStatus.AVAILABLE},
            {"name": "Avocados", "variety": "Hass Export Quality", "qty": 6500, "price": 140.0, "grade": "Export Grade", "loc": "Meru Central Packhouse", "class": CommodityClass.PERISHABLE, "status": ProduceStatus.AVAILABLE},
            {"name": "Bananas", "variety": "Cavendish Green", "qty": 8000, "price": 65.0, "grade": "Grade 1", "loc": "Kisii Ripening Store A", "class": CommodityClass.PERISHABLE, "status": ProduceStatus.AVAILABLE},
            {"name": "Mangoes", "variety": "Apple Mango Sweet", "qty": 3800, "price": 115.0, "grade": "Grade A", "loc": "Machakos Facility Room 1", "class": CommodityClass.PERISHABLE, "status": ProduceStatus.AVAILABLE},
            {"name": "Cabbages", "variety": "Gloria F1 Crisp", "qty": 9500, "price": 42.0, "grade": "Standard", "loc": "Bomet Bulk Shed C", "class": CommodityClass.PERISHABLE, "status": ProduceStatus.AVAILABLE},
            {"name": "Potatoes", "variety": "Shangi Table Stock", "qty": 14000, "price": 58.0, "grade": "Grade 1", "loc": "Nakuru Ambient Warehouse 3", "class": CommodityClass.STAPLE, "status": ProduceStatus.AVAILABLE},
            {"name": "Kale", "variety": "Sukuma Wiki Pre-Cooled", "qty": 2100, "price": 38.0, "grade": "Fresh Pick", "loc": "Kiambu Cooler 1", "class": CommodityClass.PERISHABLE, "status": ProduceStatus.AVAILABLE},
            {"name": "Onions", "variety": "Red Creole Cured", "qty": 7800, "price": 88.0, "grade": "Dry Grade A", "loc": "Nyeri Curing Facility", "class": CommodityClass.STAPLE, "status": ProduceStatus.AVAILABLE},
            {"name": "Tomatoes", "variety": "Anna F1 Greenhouse", "qty": 2900, "price": 105.0, "grade": "Premium", "loc": "Eldoret Hydroponics Store", "class": CommodityClass.PERISHABLE, "status": ProduceStatus.RESERVED},
            {"name": "Avocados", "variety": "Fuerte Local Market", "qty": 4500, "price": 85.0, "grade": "Grade 2", "loc": "Murang'a Aggregation Depot", "class": CommodityClass.PERISHABLE, "status": ProduceStatus.AVAILABLE},
            {"name": "Sweet Peppers", "variety": "California Wonder", "qty": 1800, "price": 110.0, "grade": "Grade 1", "loc": "Naivasha Packhouse 3", "class": CommodityClass.PERISHABLE, "status": ProduceStatus.AVAILABLE},
            {"name": "Passion Fruit", "variety": "Purple Granadilla", "qty": 1200, "price": 135.0, "grade": "Export Grade", "loc": "Eldoret Cold Room 1", "class": CommodityClass.PERISHABLE, "status": ProduceStatus.AVAILABLE},
        ]

        produce_objects = []
        for p in produce_items:
            harvest_dt = now - timedelta(days=random.randint(1, 6), hours=random.randint(2, 10))
            item = ProduceModel(
                id=uuid.uuid4(),
                name=p["name"],
                variety=p["variety"],
                quantity_kg=float(p["qty"]),
                unit_price=float(p["price"]),
                quality_grade=p["grade"],
                harvest_date=harvest_dt,
                storage_location=p["loc"],
                commodity_class=p["class"],
                cooperative_id=coop_user.id,
                status=p["status"],
                created_at=harvest_dt,
                updated_at=harvest_dt,
            )
            session.add(item)
            produce_objects.append(item)

        print(f"Created {len(produce_objects)} verified produce inventory items.")

        await session.commit()
        print("=== DATABASE SEED COMPLETE: SUCCESS ===")

if __name__ == "__main__":
    asyncio.run(seed())
