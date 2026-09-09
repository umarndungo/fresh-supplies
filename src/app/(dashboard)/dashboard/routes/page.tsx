"use client";

import { useState, useMemo } from "react";
import { Filter, X, MapPin, Truck, BarChart2, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { PageHeader } from "@/components/common/page-header";
import { ShipmentMap } from "@/components/map/shipment-map";
import { useShipments } from "@/hooks/use-shipments";
import { useAllMarketRecommendations } from "@/hooks/use-analytics";
import type { Shipment } from "@/types/shipment.types";
import type { MarketRecommendationOut } from "@/types/ml.types";

const RISK_TIERS = ["all", "Fresh", "At-Risk", "Critical"] as const;

export default function RoutesPage() {
  const { data: shipments, isLoading, isError, refetch } = useShipments();
  const { data: allRecommendations, isLoading: isRecLoading } = useAllMarketRecommendations(shipments ?? []);

  const [filterRiskTier, setFilterRiskTier] = useState<"all" | "Fresh" | "At-Risk" | "Critical">("all");
  const [filterCrop, setFilterCrop] = useState<string>("");
  const [selectedShipmentId, setSelectedShipmentId] = useState<string | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<MarketRecommendationOut | null>(null);

  // Merge shipment data with market recommendations
  const shipmentsWithData = useMemo(() => {
    return (shipments ?? []).map((shipment) => ({
      ...shipment,
      recommendations: allRecommendations?.[shipment.id] ?? [],
    }));
  }, [shipments, allRecommendations]);

  // Get unique crops for filter dropdown
  const crops = useMemo(() => {
    const cropSet = new Set(shipmentsWithData.map((s) => s.produceType).filter(Boolean));
    return Array.from(cropSet).sort();
  }, [shipmentsWithData]);

  // Filter shipments client-side
  const filteredShipments = useMemo(() => {
    return shipmentsWithData.filter((shipment) => {
      if (filterRiskTier !== "all" && shipment.riskTier !== filterRiskTier) return false;
      if (filterCrop && shipment.produceType?.toLowerCase() !== filterCrop.toLowerCase()) return false;
      return true;
    });
  }, [shipmentsWithData, filterRiskTier, filterCrop]);

  const hasActiveFilters = filterRiskTier !== "all" || filterCrop !== "";

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Route Optimization" description="Visualize and optimize shipment routes across the network" />
        <Card><CardContent className="h-[500px] flex items-center justify-center text-muted-foreground">Loading routes...</CardContent></Card>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="space-y-6">
        <PageHeader title="Route Optimization" description="Visualize and optimize shipment routes across the network" />
        <Card>
          <CardContent className="flex items-center justify-center h-[500px]">
            <button onClick={() => void refetch()} className="btn btn-outline">Retry</button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Route Optimization"
        description="Visualize shipment routes, filter by risk and crop, and identify optimization opportunities"
        actions={
          <div className="flex items-center gap-2">
            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={() => { setFilterRiskTier("all"); setFilterCrop(""); }}>
                <X className="size-4 mr-1" />
                Clear filters
              </Button>
            )}
          </div>
        }
      />

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Shipments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{shipmentsWithData.length}</span>
              <Truck className="size-6 text-muted-foreground" />
            </div>
            <p className="text-xs text-muted-foreground">{filteredShipments.length} after filters</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">At-Risk / Critical</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold text-destructive">
                {shipmentsWithData.filter((s) => s.riskTier === "At-Risk" || s.riskTier === "Critical").length}
              </span>
              <AlertTriangle className="size-6 text-destructive" />
            </div>
            <p className="text-xs text-muted-foreground">Require attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">With Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold text-primary">
                {shipmentsWithData.filter((s) => (allRecommendations?.[s.id]?.length ?? 0) > 0).length}
              </span>
              <BarChart2 className="size-6 text-primary" />
            </div>
            <p className="text-xs text-muted-foreground">ML-optimized routes</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Unique Crops</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{crops.length}</span>
              <MapPin className="size-6 text-muted-foreground" />
            </div>
            <p className="text-xs text-muted-foreground">Crop types in network</p>
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <div className="w-[180px]">
          <Select value={filterRiskTier} onValueChange={(v) => setFilterRiskTier(v as "all" | "Fresh" | "At-Risk" | "Critical")}>
            <SelectTrigger>
              <SelectValue placeholder="All risk tiers" />
            </SelectTrigger>
            <SelectContent>
              {RISK_TIERS.map((tier) => (
                <SelectItem key={tier} value={tier}>
                  {tier === "all" ? "All Risk Tiers" : `Risk: ${tier}`}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="w-[180px]">
          <Select value={filterCrop} onValueChange={setFilterCrop}>
            <SelectTrigger>
              <SelectValue placeholder="All crops" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Crops</SelectItem>
              {crops.map((crop) => (
                <SelectItem key={crop} value={crop}>{crop}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {hasActiveFilters && (
          <Button variant="outline" size="sm" onClick={() => { setFilterRiskTier("all"); setFilterCrop(""); }}>
            <X className="size-4 mr-1" />
            Clear filters
          </Button>
        )}
      </div>

      <Card className="h-[600px]">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="size-5" />
            Network Route Map
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0 h-[540px]">
          <ShipmentMap
            shipments={filteredShipments.map((s) => ({
              id: s.id,
              origin: s.originLatitude && s.originLongitude 
                ? { lat: s.originLatitude, lng: s.originLongitude, name: s.origin } 
                : { lat: -1.2921, lng: 36.8219, name: s.origin },
              destination: s.destinationLatitude && s.destinationLongitude 
                ? { lat: s.destinationLatitude, lng: s.destinationLongitude, name: s.destination } 
                : { lat: -1.2921, lng: 36.8219, name: s.destination },
              recommendations: allRecommendations?.[s.id] ?? [],
              produceType: s.produceType,
              status: s.status,
              riskTier: s.riskTier,
            }))}
            filterRiskTier={filterRiskTier}
            filterCrop={filterCrop}
            height="540px"
            showAllMarkets={true}
            onShipmentClick={setSelectedShipmentId}
            onRouteClick={setSelectedRoute}
          />
        </CardContent>
      </Card>

      {(selectedShipmentId || selectedRoute) && (
        <Card>
          <CardHeader>
            <CardTitle>Selected Route Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {selectedShipmentId && (() => {
              const shipment = shipmentsWithData.find((item) => item.id === selectedShipmentId);
              return shipment ? (
                <p><span className="font-medium">Shipment:</span> {shipment.produceType} · {shipment.origin} → {shipment.destination} · {shipment.status}</p>
              ) : null;
            })()}
            {selectedRoute && (
              <>
                <p><span className="font-medium">Optimization:</span> {selectedRoute.market_name} ({selectedRoute.region})</p>
                <p className="text-muted-foreground">
                  {selectedRoute.distance_km.toFixed(1)} km · {selectedRoute.duration_minutes !== undefined ? `${(selectedRoute.duration_minutes / 60).toFixed(1)} hours` : "duration unavailable"} · {selectedRoute.price_per_kg.toFixed(2)} KES/kg · {selectedRoute.revenue_retained.toLocaleString()} KES retained
                </p>
                <p className="text-muted-foreground">Spoilage estimate: {(selectedRoute.spoilage_probability * 100).toFixed(1)}%</p>
              </>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Truck className="size-5" />
            Shipment Details
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-3 font-medium">ID</th>
                  <th className="text-left p-3 font-medium">Crop</th>
                  <th className="text-left p-3 font-medium">Route</th>
                  <th className="text-left p-3 font-medium">Status</th>
                  <th className="text-left p-3 font-medium">Risk Tier</th>
                  <th className="text-left p-3 font-medium">Recommendations</th>
                </tr>
              </thead>
              <tbody>
                {filteredShipments.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center p-8 text-muted-foreground">No shipments match current filters</td>
                  </tr>
                ) : (
                  filteredShipments.map((shipment) => (
                    <tr key={shipment.id} className="border-b border-border/50 hover:bg-muted/30">
                      <td className="p-3 font-mono text-xs">{shipment.id.slice(0, 8)}...</td>
                      <td className="p-3">{shipment.produceType}</td>
                      <td className="p-3">{shipment.origin} → {shipment.destination}</td>
                      <td className="p-3">
                        <Badge variant={shipment.status === "IN_TRANSIT" ? "default" : "secondary"}>
                          {shipment.status}
                        </Badge>
                      </td>
                      <td className="p-3">
                        <Badge variant={shipment.riskTier === "Critical" ? "destructive" : shipment.riskTier === "At-Risk" ? "warning" : "default"}>
                          {shipment.riskTier ?? "—"}
                        </Badge>
                      </td>
                      <td className="p-3">
                        <Badge variant="outline">
                          {allRecommendations?.[shipment.id]?.length ?? 0} markets
                        </Badge>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}