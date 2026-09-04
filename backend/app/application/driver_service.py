from datetime import datetime
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.domain.repositories import DriverRepository


class DriverService:
    def __init__(self, driver_repository: DriverRepository):
        self._driver = driver_repository

    async def get_manifest(self, date: datetime, user_id: UUID, user_role: str) -> list[dict]:
        return await self._driver.get_manifest_stops(date, user_id, user_role)

    async def confirm_stop(self, shipment_id: UUID, confirmed_at: datetime, lat: float, lon: float) -> dict:
        result = await self._driver.confirm_stop(shipment_id, confirmed_at, lat, lon)
        if result.get("status") == "not_found":
            raise NotFoundError("Shipment not found.")
        return result
