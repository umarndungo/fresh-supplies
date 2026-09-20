import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.domain.entities import OwnerType, ShipmentStatus, User
from app.domain.repositories import ShipmentSyncStagingRepository
from app.application.ml_service import predict_spoilage


class MobileShipmentService:
    def __init__(self, staging_repository: ShipmentSyncStagingRepository):
        self._staging = staging_repository

    async def sync_shipments(
        self, shipments: list[dict], user: User
    ) -> list[dict]:
        results = []
        for item in shipments:
            existing = await self._staging.get_by_client_id(item["client_id"])
            if existing:
                results.append({
                    "client_id": item["client_id"],
                    "status": "duplicate",
                    "server_id": existing.id,
                    "risk_tier": None,
                    "error": None,
                })
                continue

            owner_type = OwnerType(user.account_type.value) if user.account_type else OwnerType.INDIVIDUAL
            coop_id = user.cooperative_id if owner_type == OwnerType.COOPERATIVE else None

            try:
                staging = await self._staging.create(
                    client_id=item["client_id"],
                    crop=item["crop"],
                    quantity_kg=item["quantity_kg"],
                    captured_at=item["captured_at"],
                    location_lat=item["location"]["lat"],
                    location_lon=item["location"]["lon"],
                    photo_ref=item.get("photo_ref"),
                    photo_status="pending" if item.get("photo_ref") else None,
                    notes=item.get("notes"),
                    owner_type=owner_type,
                    cooperative_id=coop_id,
                    submitted_by_user_id=user.id,
                )
            except IntegrityError:
                # client_id is unique — a retried batch (expected on flaky
                # mobile connectivity) can race another in-flight sync of
                # the same item past the get_by_client_id check above. Roll
                # back so the session is usable for the rest of this batch,
                # then treat it the same as the ordinary duplicate case.
                await self._staging.rollback()
                existing = await self._staging.get_by_client_id(item["client_id"])
                results.append({
                    "client_id": item["client_id"],
                    "status": "duplicate",
                    "server_id": existing.id if existing else None,
                    "risk_tier": None,
                    "error": None,
                })
                continue

            risk_tier = None
            try:
                ml_input = {
                    "crop_type": item["crop"],
                    "latitude": item["location"]["lat"],
                    "longitude": item["location"]["lon"],
                    "quantity_kg": item["quantity_kg"],
                }
                prediction = predict_spoilage(ml_input)
                risk_tier = prediction.get("risk_tier")
            except Exception:
                pass

            results.append({
                "client_id": item["client_id"],
                "status": "created",
                "server_id": staging.id,
                "risk_tier": risk_tier,
                "error": None,
            })

        return results

    async def upload_photo(self, client_id: str, file: UploadFile, user: User) -> dict:
        staging = await self._staging.get_by_client_id(client_id)
        # Same "not found" framing whether the client_id doesn't exist or
        # belongs to someone else's staged capture — a client_id can leak
        # (shared device, support ticket, log line), and confirming it's
        # real but not yours would be its own small information leak.
        if not staging or staging.submitted_by_user_id != user.id:
            raise NotFoundError("Shipment with this client_id not found.")

        photo_dir = Path(settings.PHOTO_STORAGE_PATH)
        photo_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{client_id}_{uuid.uuid4().hex}.jpg"
        filepath = photo_dir / filename

        contents = await file.read()
        filepath.write_bytes(contents)

        photo_ref = f"media/shipment_photos/{filename}"
        await self._staging.update_photo_ref(client_id, photo_ref)

        return {"photo_ref": photo_ref, "status": "uploaded"}

    async def get_sync_status(
        self, since: datetime, user: User
    ) -> list[dict]:
        items = await self._staging.list_since(
            since=since,
            user_id=user.id,
        )
        return [
            {
                "client_id": item.client_id,
                "server_id": item.id,
                "status": item.reconciliation_status.value.lower(),
                "updated_at": item.sync_received_at,
            }
            for item in items
        ]
