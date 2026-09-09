"use client";

import { useState, useRef, useEffect } from "react";
import { MapPin, Map, X, ChevronDown, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { KENYAN_MARKETS, type Market } from "./kenyan-markets";
import * as L from "leaflet";
import "leaflet/dist/leaflet.css";

const DEFAULT_CENTER: [number, number] = [-0.5, 37.5];
const DEFAULT_ZOOM = 7;

const mapIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface LocationPickerProps {
  latitude: number | undefined;
  longitude: number | undefined;
  onLocationChange: (lat: number, lng: number) => void;
  label?: string;
  disabled?: boolean;
}

export function LocationPicker({ latitude, longitude, onLocationChange, label = "Location", disabled = false }: LocationPickerProps) {
  const [showMap, setShowMap] = useState(false);
  const [selectedMarket, setSelectedMarket] = useState<Market | null>(null);
  const [marker, setMarker] = useState<L.Marker | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Initialize map when dialog opens
  useEffect(() => {
    if (!showMap || mapInstanceRef.current || !mapContainerRef.current) return;

    let map: L.Map | null = null;

    try {
      map = L.map(mapContainerRef.current, {
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

      // Add click handler to map
      map.on("click", (e) => {
        const { lat, lng } = e.latlng;
        onLocationChange(lat, lng);
        updateMarker(lat, lng);
      });

      // Add existing marker if coordinates exist
      if (latitude !== undefined && longitude !== undefined) {
        updateMarker(latitude, longitude);
      }
    } catch (err) {
      console.error("Failed to initialize map:", err);
    }

    return () => {
      if (map) {
        map.remove();
      }
    };
  }, [showMap]);

  // Update marker position
  const updateMarker = (lat: number, lng: number) => {
    if (!mapInstanceRef.current) return;

    if (marker) {
      marker.setLatLng([lat, lng]);
    } else {
      const newMarker = L.marker([lat, lng], { icon: mapIcon })
        .bindPopup(`Selected: ${lat.toFixed(4)}, ${lng.toFixed(4)}`);
      newMarker.addTo(mapInstanceRef.current!);
      setMarker(newMarker);
    }
    mapInstanceRef.current!.setView([lat, lng], 10);
  };

  // Handle market selection from dropdown
  const handleMarketSelect = (market: Market) => {
    setSelectedMarket(market);
    onLocationChange(market.latitude, market.longitude);
    if (mapInstanceRef.current) {
      updateMarker(market.latitude, market.longitude);
    }
  };

  // Clear selected location
  const handleClear = () => {
    setSelectedMarket(null);
    if (marker && mapInstanceRef.current) {
      mapInstanceRef.current.removeLayer(marker);
      setMarker(null);
    }
    onLocationChange(Number.NaN, Number.NaN);
  };

  // Filter markets based on search query
  const filteredMarkets = KENYAN_MARKETS.filter((market) =>
    market.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    market.region.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-3">
      <Label className="text-sm font-medium">{label}</Label>

      {/* Current coordinates display */}
      <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg">
        <MapPin className="size-4 text-muted-foreground" />
        <div className="flex-1 text-sm">
          {latitude !== undefined && longitude !== undefined ? (
            <>
              <span className="font-mono">
                {latitude.toFixed(4)}, {longitude.toFixed(4)}
              </span>
              {selectedMarket && (
                <span className="ml-2 text-muted-foreground">
                  ({selectedMarket.name}, {selectedMarket.region})
                </span>
              )}
            </>
          ) : (
            <span className="text-muted-foreground">No location selected</span>
          )}
        </div>
        {(latitude !== undefined || longitude !== undefined) && !disabled && (
          <Button type="button" variant="ghost" size="icon" onClick={handleClear} aria-label="Clear location">
            <X className="size-4 text-muted-foreground" />
          </Button>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex gap-2">
        {/* Market dropdown */}
        <div className="w-[250px]">
          <Select value={selectedMarket?.id ?? ""} onValueChange={(v) => {
            const market = KENYAN_MARKETS.find((m) => m.id === v);
            if (market) handleMarketSelect(market);
          }}>
            <SelectTrigger>
              <SelectValue placeholder="Select Kenyan market..." />
            </SelectTrigger>
            <SelectContent>
              {KENYAN_MARKETS.map((market) => (
                <SelectItem key={market.id} value={market.id}>
                  {market.name} ({market.region})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Map picker dialog */}
        <Dialog open={showMap} onOpenChange={setShowMap}>
          <DialogTrigger asChild>
            <Button type="button" variant="outline" disabled={disabled}>
              <Map className="size-4 mr-2" />
              Pick on Map
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[80vh] p-0">
            <DialogHeader>
              <DialogTitle className="flex items-center justify-between">
                <span>Pick Location on Map</span>
                <div className="flex items-center gap-2">
                  <Input
                    placeholder="Search markets..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-[200px]"
                  />
                  <Button variant="ghost" size="icon" onClick={() => setShowMap(false)} aria-label="Close">
                    <X className="size-4" />
                  </Button>
                </div>
              </DialogTitle>
            </DialogHeader>
            <div className="p-0">
              <div className="border-t">
                {/* Quick select markets */}
                <div className="p-3 border-b bg-muted/30">
                  <Label className="text-sm font-medium mb-2 block">Quick Select Market</Label>
                  <Select
                    value=""
                    onValueChange={(v) => {
                      const market = KENYAN_MARKETS.find((m) => m.id === v);
                      if (market) handleMarketSelect(market);
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a market..." />
                    </SelectTrigger>
                    <SelectContent>
                      {filteredMarkets.map((market) => (
                        <SelectItem key={market.id} value={market.id}>
                          {market.name} ({market.region})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                {/* Map */}
                <div ref={mapContainerRef} style={{ height: "400px", width: "100%" }} />
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}

export function LocationPickerField({
  latitude,
  longitude,
  onChange,
  label = "Location",
  disabled = false,
}: LocationPickerProps & { onChange: (lat: number | undefined, lng: number | undefined) => void }) {
  return (
    <LocationPicker
      latitude={latitude}
      longitude={longitude}
      onLocationChange={(lat, lng) => onChange(lat === 0 && lng === 0 ? undefined : lat, lng === 0 && lng === 0 ? undefined : lng)}
      label={label}
      disabled={disabled}
    />
  );
}