from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from app.api.deps import get_current_user
from app.application.ml_schemas import (
    MarketRecommendationOut,
    MarketRecommendationRequest,
    SpoilageRequest,
    SuspicionOut,
)
from app.application.ml_service import predict_spoilage, recommend_market

# /ml endpoints require a valid bearer token (same auth as shipments/produce).
# ML inference itself is stateless, but exposing it without auth would let
# anyone burn compute / probe the model; auth mirrors the rest of the API.
router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/predict-spoilage", response_model=SuspicionOut, dependencies=[Depends(get_current_user)])
async def predict_spoilage_route(payload: SpoilageRequest):
    result = await run_in_threadpool(predict_spoilage, payload.model_dump())
    return SuspicionOut(**result)


@router.post("/recommend-market", response_model=list[MarketRecommendationOut], dependencies=[Depends(get_current_user)])
async def recommend_market_route(payload: MarketRecommendationRequest):
    result = await run_in_threadpool(
        recommend_market, payload.model_dump(), payload.top_n
    )
    return [MarketRecommendationOut(**r) for r in result]
