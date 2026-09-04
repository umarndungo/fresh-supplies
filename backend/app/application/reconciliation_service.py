import logging

from app.domain.entities import ReconciliationStatus, ShipmentStatus
from app.infrastructure.db import async_session_factory
from app.infrastructure.models import ShipmentSyncStagingModel, ShipmentModel
from app.infrastructure.shipment_sync_repository import SqlAlchemyShipmentSyncStagingRepository

logger = logging.getLogger("freshroute.reconciliation")


async def run_reconciliation() -> dict:
    async with async_session_factory() as session:
        staging_repo = SqlAlchemyShipmentSyncStagingRepository(session)
        pending = await staging_repo.list_pending_reconciliation(limit=50)

        created = 0
        failed = 0

        for item in pending:
            try:
                shipment = ShipmentModel(
                    origin=f"Lat:{item.location_lat}, Lon:{item.location_lon}",
                    destination="Pending",
                    produce_type=item.crop,
                    status=ShipmentStatus.SCHEDULED,
                    scheduled_date=item.captured_at,
                    created_by=item.submitted_by_user_id,
                    owner_type=item.owner_type,
                    cooperative_id=item.cooperative_id,
                    submitted_by_user_id=item.submitted_by_user_id,
                    photo_ref=item.photo_ref,
                    photo_status=item.photo_status,
                    client_id=item.client_id,
                )
                session.add(shipment)
                await session.flush()
                await staging_repo.mark_reconciled(item.id, shipment.id)
                created += 1
            except Exception as exc:
                logger.error("Reconciliation failed for %s: %s", item.client_id, exc)
                await staging_repo.mark_failed(item.id)
                failed += 1

        await session.commit()
        return {"created": created, "failed": failed, "total_pending": len(pending)}
