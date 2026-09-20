from uuid import UUID

from app.application.tenancy import require_not_administrator, scope_for
from app.core.exceptions import NotFoundError
from app.core.i18n import get_risk_label
from app.domain.entities import User
from app.domain.repositories import CooperativeAccessGrantRepository, ShipmentRepository
from app.application.ml_service import recommend_market


class MobileRecommendationService:
    def __init__(self, shipment_repository: ShipmentRepository, grants: CooperativeAccessGrantRepository):
        self._shipments = shipment_repository
        self._grants = grants

    async def get_recommendation(
        self,
        shipment_id: UUID,
        crop: str,
        quantity_kg: float,
        lat: float,
        lon: float,
        actor: User,
        locale: str = "en",
    ) -> dict:
        require_not_administrator(actor)
        shipment = await self._shipments.get_by_id(shipment_id)
        scope = await scope_for(actor, self._grants)
        if not shipment or not scope.covers(
            owner_type=shipment.owner_type,
            cooperative_id=shipment.cooperative_id,
            created_by=shipment.created_by,
            driver_user_id=shipment.driver_user_id,
        ):
            # Same "not found" framing as ShipmentService.get_shipment — a
            # 403 here would confirm the ID belongs to someone else's
            # shipment even though this caller can't otherwise reach it.
            raise NotFoundError("Shipment not found.")

        try:
            ml_input = {
                "crop_type": crop,
                "latitude": lat,
                "longitude": lon,
                "quantity_kg": quantity_kg,
            }
            markets = recommend_market(ml_input, top_n=3)
        except Exception:
            markets = []

        risk_tier = "FRESH"
        if markets:
            proba = markets[0].get("spoilage_probability", 0.0)
            risk_tier = "CRITICAL" if proba >= 0.6 else ("AT_RISK" if proba >= 0.35 else "FRESH")

        risk_label = get_risk_label(risk_tier, locale)

        recommended = None
        alternates = []
        if markets:
            top = markets[0]
            recommended = {
                "name": top["market_name"],
                "distance_km": top["distance_km"],
                "est_price_per_kg": top["price_per_kg"],
                "est_revenue_retained": top["revenue_retained"],
            }
            for m in markets[1:3]:
                alternates.append({
                    "name": m["market_name"],
                    "distance_km": m["distance_km"],
                    "est_price_per_kg": m["price_per_kg"],
                    "est_revenue_retained": m["revenue_retained"],
                })

        return {
            "risk_tier": risk_tier,
            "risk_label": risk_label,
            "recommended_market": recommended,
            "alternate_markets": alternates,
        }
