"use client";

import { useEffect, useRef, useState } from "react";
import * as L from "leaflet";
import "leaflet/dist/leaflet.css";
import { KENYAN_MARKETS, type Market } from "@/components/map/kenyan-markets";
import type { MarketRecommendationOut } from "@/types/ml.types";
import type { Shipment } from "@/types/shipment.types";

const DEFAULT_CENTER: [number, number] = [-0.5, 37.5];
const DEFAULT_ZOOM = 7;

const marketIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const recommendedMarketIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [30, 50],
  iconAnchor: [15, 50],
  popupAnchor: [1, -42],
  shadowSize: [41, 41],
  className: "leaflet-marker-recommended",
});

const originIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
  className: "leaflet-marker-origin",
});

const ROUTE_COLORS = [
  "#3b82f6", // blue
  "#ef4444", // red
  "#22c55e", // green
  "#f59e0b", // amber
  "#a855f7", // purple
  "#ec4899", // pink
  "#06b6d4", // cyan
  "#f97316", // orange
];

function isValidRouteGeometry(
  geometry: MarketRecommendationOut["route_geometry"]
): geometry is { type: "LineString"; coordinates: [number, number][] } {
  return Boolean(
    geometry?.type === "LineString" &&
      geometry.coordinates.length >= 2 &&
      geometry.coordinates.every(
        ([lng, lat]) =>
          Number.isFinite(lat) && Number.isFinite(lng) &&
          lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180
      )
  );
}

function isValidCoordinate(
  point: { lat: number; lng: number } | null | undefined
): point is { lat: number; lng: number } {
  return Boolean(
    point &&
      Number.isFinite(point.lat) &&
      Number.isFinite(point.lng) &&
      point.lat >= -90 &&
      point.lat <= 90 &&
      point.lng >= -180 &&
      point.lng <= 180
  );
}

interface ShipmentMapProps {
  // Legacy single shipment props
  origin?: { lat: number; lng: number; name?: string };
  destination?: { lat: number; lng: number; name?: string };
  recommendations?: MarketRecommendationOut[];
  showAllMarkets?: boolean;
  height?: string;
  // New multi-shipment props
  shipments?: Array<{
    id: string;
    origin: { lat: number; lng: number; name?: string };
    destination: { lat: number; lng: number; name?: string };
    recommendations?: MarketRecommendationOut[];
    produceType?: string;
    status?: string;
    riskTier?: "Fresh" | "At-Risk" | "Critical";
  }>;
  filterRiskTier?: "Fresh" | "At-Risk" | "Critical" | "all";
  filterCrop?: string;
  onRouteClick?: (recommendation: MarketRecommendationOut) => void;
  onShipmentClick?: (shipmentId: string) => void;
}

export function ShipmentMap({
  origin,
  destination,
  recommendations = [],
  showAllMarkets = true,
  height = "400px",
  shipments = [],
  filterRiskTier = "all",
  filterCrop,
  onRouteClick,
  onShipmentClick,
}: ShipmentMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Marker[]>([]);
  const routeLayersRef = useRef<L.Polyline[]>([]);
  const [mapError, setMapError] = useState<string | null>(null);

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    try {
      const map = L.map(mapRef.current, {
        center: DEFAULT_CENTER,
        zoom: DEFAULT_ZOOM,
        zoomControl: true,
        attributionControl: true,
      });

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);

      mapInstanceRef.current = map;

      map.on("load", () => {
        setTimeout(() => map.invalidateSize(), 0);
      });
    } catch (err) {
      setMapError("Failed to initialize map");
      console.error(err);
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear existing markers and routes
    markersRef.current.forEach((marker) => map.removeLayer(marker));
    markersRef.current = [];

    routeLayersRef.current.forEach((layer) => map.removeLayer(layer));
    routeLayersRef.current = [];

    const bounds: [number, number][] = [];

    // Determine if we're in multi-shipment mode
    const isMultiShipment = shipments.length > 0;
    const activeShipments = isMultiShipment ? shipments : [{
      id: "single",
      origin,
      destination,
      recommendations,
      produceType: undefined,
      status: undefined,
      riskTier: undefined,
    }];

    // Filter shipments
    const filteredShipments = activeShipments.filter((shipment) => {
      if (filterRiskTier !== "all" && shipment.riskTier && shipment.riskTier !== filterRiskTier) {
        return false;
      }
      if (filterCrop && shipment.produceType && shipment.produceType.toLowerCase() !== filterCrop.toLowerCase()) {
        return false;
      }
      return true;
    });

    // Show all markets if enabled (only in single shipment mode or when no shipments)
    if (showAllMarkets && !isMultiShipment) {
      KENYAN_MARKETS.forEach((market) => {
        const isRecommended = recommendations.some((r) => r.market_id === market.id);
        const isDestination = destination && market.id === destination.name?.toLowerCase().replace(/\s+/g, "-");

        const marker = L.marker([market.latitude, market.longitude], {
          icon: isRecommended || isDestination ? recommendedMarketIcon : marketIcon,
        }).bindPopup(
          `<strong>${market.name}</strong><br/>${market.region}<br/>
           ${isRecommended ? "★ Recommended" : ""}
           ${isDestination ? "📍 Destination" : ""}`
        );
        marker.addTo(map);
        markersRef.current.push(marker);
        bounds.push([market.latitude, market.longitude]);
      });
    }

    // Render each shipment
    filteredShipments.forEach((shipment, index) => {
      const color = ROUTE_COLORS[index % ROUTE_COLORS.length];
      const shipmentRecs = shipment.recommendations ?? [];
      const validOrigin = isValidCoordinate(shipment.origin) ? shipment.origin : undefined;
      const validDestination = isValidCoordinate(shipment.destination)
        ? shipment.destination
        : undefined;

      // Origin marker
      if (validOrigin) {
        const marker = L.marker([validOrigin.lat, validOrigin.lng], { icon: originIcon })
          .bindPopup(
            `<strong>Origin</strong><br/>${validOrigin.name ?? "Shipment Origin"}<br/>
             ${shipment.produceType ? `Crop: ${shipment.produceType}` : ""}
             ${shipment.riskTier ? `Risk: ${shipment.riskTier}` : ""}`
          );
        marker.addTo(map);
        markersRef.current.push(marker);
        bounds.push([validOrigin.lat, validOrigin.lng]);
      }

      // Destination marker
      if (validDestination) {
        const marker = L.marker([validDestination.lat, validDestination.lng], { icon: recommendedMarketIcon })
          .bindPopup(`<strong>Destination</strong><br/>${validDestination.name ?? "Shipment Destination"}`);
        marker.addTo(map);
        markersRef.current.push(marker);
        bounds.push([validDestination.lat, validDestination.lng]);
      }

      // Route line
      if (validOrigin && validDestination) {
        const route = L.polyline(
          [
            [validOrigin.lat, validOrigin.lng],
            [validDestination.lat, validDestination.lng],
          ],
          { color, weight: 3, opacity: 0.7, dashArray: "10, 10" }
        ).addTo(map);
        route.on("click", () => onShipmentClick?.(shipment.id));
        routeLayersRef.current.push(route);
        bounds.push(
          [validOrigin.lat, validOrigin.lng],
          [validDestination.lat, validDestination.lng]
        );
      }

      // Recommended markets for this shipment
      shipmentRecs.forEach((rec) => {
        const market = KENYAN_MARKETS.find((m) => m.id === rec.market_id);
        if (market && (!showAllMarkets || isMultiShipment)) {
          const marker = L.marker([market.latitude, market.longitude], { icon: recommendedMarketIcon })
            .bindPopup(
              `<strong>${market.name}</strong><br/>${market.region}<br/>
               Price: ${rec.price_per_kg.toFixed(2)} KES/kg<br/>
               Distance: ${rec.distance_km.toFixed(1)} km<br/>
               Spoilage: ${(rec.spoilage_probability * 100).toFixed(1)}%<br/>
               Revenue: ${rec.revenue_retained.toLocaleString()} KES`
            );
          marker.addTo(map);
          markersRef.current.push(marker);
          bounds.push([market.latitude, market.longitude]);
        }
      });

      const recommendedRoute = shipmentRecs.find((rec) => isValidRouteGeometry(rec.route_geometry));
      if (recommendedRoute && isValidRouteGeometry(recommendedRoute.route_geometry)) {
        const route = L.polyline(
          recommendedRoute.route_geometry.coordinates.map(([lng, lat]) => [lat, lng] as [number, number]),
          { color: "#16a34a", weight: 5, opacity: 0.85 }
        ).addTo(map);
        route.on("click", () => {
          onShipmentClick?.(shipment.id);
          onRouteClick?.(recommendedRoute);
        });
        routeLayersRef.current.push(route);
        recommendedRoute.route_geometry.coordinates.forEach(([lng, lat]) => bounds.push([lat, lng]));
      }
    });

    if (bounds.length > 0) {
      map.fitBounds(bounds as L.LatLngBoundsExpression, { padding: [50, 50] });
    }
  }, [origin, destination, recommendations, showAllMarkets, shipments, filterRiskTier, filterCrop, onRouteClick, onShipmentClick]);

  if (mapError) {
    return (
      <div className="rounded-xl border border-border bg-card p-8 text-center">
        <p className="text-destructive">{mapError}</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <div ref={mapRef} style={{ height, width: "100%" }} />
    </div>
  );
}

export function MiniMarketMap({ marketId, height = "200px" }: { marketId: string; height?: string }) {
  const market = KENYAN_MARKETS.find((m) => m.id === marketId);
  if (!market) return null;

  return (
    <ShipmentMap
      destination={{ lat: market.latitude, lng: market.longitude, name: market.name }}
      showAllMarkets={false}
      height={height}
    />
  );
}