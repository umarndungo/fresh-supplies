"use client";

import { useState, useEffect } from "react";
import { MapPin, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { searchLocationsRequest } from "@/lib/api/locations.api";
import type { LocationSearchResult } from "@/types/location.types";

interface LocationPickerProps {
  latitude: number | undefined;
  longitude: number | undefined;
  onLocationChange: (lat: number, lng: number) => void;
  label?: string;
  disabled?: boolean;
  searchQuery?: string;
}

export function LocationPicker({ latitude, longitude, onLocationChange, label = "Location", disabled = false, searchQuery = "" }: LocationPickerProps) {
  const [selectedPlace, setSelectedPlace] = useState<LocationSearchResult | null>(null);
  const [searchResults, setSearchResults] = useState<LocationSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState(false);

  useEffect(() => {
    const normalizedQuery = searchQuery.trim();
    if (normalizedQuery.length < 2) {
      setSearchResults([]);
      setSearchError(false);
      setIsSearching(false);
      return;
    }

    let active = true;
    const timeout = window.setTimeout(async () => {
      setIsSearching(true);
      setSearchError(false);
      try {
        const results = await searchLocationsRequest(normalizedQuery);
        if (active) setSearchResults(results);
      } catch {
        if (active) {
          setSearchResults([]);
          setSearchError(true);
        }
      } finally {
        if (active) setIsSearching(false);
      }
    }, 400);

    return () => {
      active = false;
      window.clearTimeout(timeout);
    };
  }, [searchQuery]);

  const handleLocationSelect = (place: LocationSearchResult) => {
    setSelectedPlace(place);
    onLocationChange(place.latitude, place.longitude);
  };

  // Clear selected location
  const handleClear = () => {
    setSelectedPlace(null);
    onLocationChange(Number.NaN, Number.NaN);
  };

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
              {selectedPlace && (
                <span className="ml-2 text-muted-foreground">
                  ({selectedPlace.display_name})
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

      {searchQuery.trim().length >= 2 && (
        <div className="space-y-2 rounded-lg border border-border/60 bg-muted/20 p-2">
          <div className="flex items-center gap-2 px-2 text-xs text-muted-foreground">
            {isSearching ? <Loader2 className="size-3 animate-spin" /> : <MapPin className="size-3" />}
            {isSearching ? "Searching Kenyan locations..." : "Select the pickup location"}
          </div>
          {searchResults.map((place) => (
            <button
              key={`${place.latitude}-${place.longitude}-${place.display_name}`}
              type="button"
              className="w-full rounded-md px-2 py-2 text-left text-sm hover:bg-muted"
              onClick={() => handleLocationSelect(place)}
            >
              <span className="block font-medium">{place.display_name}</span>
              <span className="text-xs text-muted-foreground">
                {place.county ? `${place.county} · ` : ""}{place.latitude.toFixed(4)}, {place.longitude.toFixed(4)}
              </span>
            </button>
          ))}
          {!isSearching && !searchError && searchResults.length === 0 && (
            <p className="px-2 py-1 text-xs text-muted-foreground">No Kenyan locations found. Try a nearby town or include the county.</p>
          )}
          {searchError && <p className="px-2 py-1 text-xs text-destructive">Location search is unavailable. Use the map to select the pickup point.</p>}
        </div>
      )}

      <p className="text-xs text-muted-foreground">
        Search and select a Kenyan pickup location above. Its coordinates will be used for ML predictions.
      </p>
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