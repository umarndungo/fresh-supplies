"use client";

import { useEffect, useRef, useState } from "react";
import * as L from "leaflet";
import "leaflet/dist/leaflet.css";
import { KENYAN_MARKETS, type Market } from "@/components/map/kenyan-markets";
import type { MarketRecommendationOut } from "@/types/ml.types";

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

interface ShipmentMapProps {
  origin?: { lat: number; lng: number; name?: string };
  destination?: { lat: number; lng: number; name?: string };
  recommendations?: MarketRecommendationOut[];
  showAllMarkets?: boolean;
  height?: string;
}

export function ShipmentMap({
  origin,
  destination,
  recommendations = [],
  showAllMarkets = true,
  height = "400px",
}: ShipmentMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Marker[]>([]);
  const routeLayerRef = useRef<L.Polyline | null>(null);
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

    markersRef.current.forEach((marker) => map.removeLayer(marker));
    markersRef.current = [];

    if (routeLayerRef.current) {
      map.removeLayer(routeLayerRef.current);
      routeLayerRef.current = null;
    }

    const bounds: [number, number][] = [];

    if (showAllMarkets) {
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

    if (origin) {
      const marker = L.marker([origin.lat, origin.lng], { icon: originIcon })
        .bindPopup(`<strong>Origin</strong><br/>${origin.name ?? "Shipment Origin"}`);
      marker.addTo(map);
      markersRef.current.push(marker);
      bounds.push([origin.lat, origin.lng]);
    }

    if (destination) {
      const marker = L.marker([destination.lat, destination.lng], { icon: recommendedMarketIcon })
        .bindPopup(`<strong>Destination</strong><br/>${destination.name ?? "Shipment Destination"}`);
      marker.addTo(map);
      markersRef.current.push(marker);
      bounds.push([destination.lat, destination.lng]);
    }

    if (origin && destination) {
      const route = L.polyline(
        [
          [origin.lat, origin.lng],
          [destination.lat, destination.lng],
        ],
        { color: "#3b82f6", weight: 3, opacity: 0.7, dashArray: "10, 10" }
      ).addTo(map);
      routeLayerRef.current = route;
      bounds.push([origin.lat, origin.lng], [destination.lat, destination.lng]);
    }

    recommendations.forEach((rec) => {
      const market = KENYAN_MARKETS.find((m) => m.id === rec.market_id);
      if (market && !showAllMarkets) {
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

    if (bounds.length > 0) {
      map.fitBounds(bounds as L.LatLngBoundsExpression, { padding: [50, 50] });
    }
  }, [origin, destination, recommendations, showAllMarkets]);

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