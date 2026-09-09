import time
from typing import Annotated
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_user
from app.application.location_schemas import LocationSearchResult
from app.core.config import settings

router = APIRouter(prefix="/locations", tags=["locations"])
_CACHE_TTL_SECONDS = 300
_search_cache: dict[str, tuple[float, list[LocationSearchResult]]] = {}


@router.get(
    "/search",
    response_model=list[LocationSearchResult],
    responses={502: {"description": "Location provider unavailable"}},
    dependencies=[Depends(get_current_user)],
)
async def search_locations(query: Annotated[str, Query(min_length=2, max_length=100)]):
    normalized_query = " ".join(query.split()).lower()
    cached = _search_cache.get(normalized_query)
    if cached and time.monotonic() - cached[0] < _CACHE_TTL_SECONDS:
        return cached[1]

    params = {
        "q": normalized_query,
        "format": "jsonv2",
        "addressdetails": "1",
        "limit": "6",
        "countrycodes": "ke",
    }
    headers = {"User-Agent": settings.GEOCODING_USER_AGENT}

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(settings.GEOCODING_URL, params=params, headers=headers)
            response.raise_for_status()
            payload: list[dict[str, Any]] = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="Location search is temporarily unavailable.") from exc

    results = [
        LocationSearchResult(
            display_name=item.get("display_name", normalized_query),
            latitude=float(item["lat"]),
            longitude=float(item["lon"]),
            type=item.get("type"),
            county=(item.get("address") or {}).get("county"),
        )
        for item in payload
        if item.get("lat") is not None and item.get("lon") is not None
    ]
    _search_cache[normalized_query] = (time.monotonic(), results)
    return results