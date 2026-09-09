from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Protocol


@dataclass(frozen=True)
class Coordinate:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class RouteResult:
    distance_km: float
    duration_minutes: float
    geometry: dict
    provider: str
    estimated: bool


class RoutingProvider(Protocol):
    def get_route(self, origin: Coordinate, destination: Coordinate) -> RouteResult:
        ...


def haversine_km(origin: Coordinate, destination: Coordinate) -> float:
    radius_km = 6371.0
    lat1, lat2 = radians(origin.latitude), radians(destination.latitude)
    delta_lat = radians(destination.latitude - origin.latitude)
    delta_lon = radians(destination.longitude - origin.longitude)
    value = (
        sin(delta_lat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    )
    return radius_km * 2 * asin(sqrt(value))


class StraightLineRoutingProvider:
    """Offline fallback for local development and deterministic tests."""

    def __init__(self, average_speed_kmh: float = 35.0, road_multiplier: float = 1.25):
        self.average_speed_kmh = average_speed_kmh
        self.road_multiplier = road_multiplier

    def get_route(self, origin: Coordinate, destination: Coordinate) -> RouteResult:
        straight_line_distance = haversine_km(origin, destination)
        distance_km = straight_line_distance * self.road_multiplier
        duration_minutes = distance_km / self.average_speed_kmh * 60
        return RouteResult(
            distance_km=round(distance_km, 2),
            duration_minutes=round(duration_minutes, 1),
            geometry={
                "type": "LineString",
                "coordinates": [
                    [origin.longitude, origin.latitude],
                    [destination.longitude, destination.latitude],
                ],
            },
            provider="straight-line",
            estimated=True,
        )