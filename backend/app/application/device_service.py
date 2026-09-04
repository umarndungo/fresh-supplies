from uuid import UUID

from app.domain.repositories import DeviceTokenRepository


class DeviceService:
    def __init__(self, device_repository: DeviceTokenRepository):
        self._devices = device_repository

    async def register_device(self, user_id: UUID, device_token: str, platform: str) -> dict:
        await self._devices.register(user_id=user_id, device_token=device_token, platform=platform)
        return {"status": "registered"}
