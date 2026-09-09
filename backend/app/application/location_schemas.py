from pydantic import BaseModel


class LocationSearchResult(BaseModel):
    display_name: str
    latitude: float
    longitude: float
    type: str | None = None
    county: str | None = None