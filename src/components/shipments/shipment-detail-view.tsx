"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { ArrowLeft, Truck, MapPin, Calendar, Package, Thermometer, Gauge, Scale, AlertCircle, CheckCircle, XCircle, Loader2, Trash2, Map } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/empty-state";
import { ErrorState } from "@/components/common/error-state";
import { PageHeader } from "@/components/common/page-header";
import { RiskTierBadge, getRiskTierFromProbability } from "@/components/shipments/risk-tier-badge";
import { usePredictSpoilage, useRecommendMarket } from "@/hooks/use-ml";
import { useShipment, useDeleteShipment, useUpdateShipment } from "@/hooks/use-shipments";
import { useRouter } from "next/navigation";
import { formatDate } from "@/lib/utils";
import { KENYAN_MARKETS } from "@/components/map/kenyan-markets";
import type { Shipment } from "@/types/shipment.types";
import type { MarketRecommendationOut } from "@/types/ml.types";

const ShipmentMap = dynamic(
  () => import("@/components/map/shipment-map").then((module) => module.ShipmentMap),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[500px] items-center justify-center rounded-xl border border-border bg-card text-sm text-muted-foreground">
        Loading map...
      </div>
    ),
  }
);

function buildSpoilageRequest(shipment: Shipment) {
  return {
    crop_type: shipment.produceType,
    latitude: shipment.originLatitude ?? -1.2921,
    longitude: shipment.originLongitude ?? 36.8219,
    Temperature_C: shipment.temperatureC ?? 25,
    Transit_Duration_Hr: shipment.transitDurationHr ?? 4,
    Pressure_PSI: shipment.pressurePsi ?? 30,
    baseline_loss_pct: shipment.baselineLossPct ?? 10,
    quantity_kg: shipment.quantityKg ?? 100,
  };
}

function buildMarketRequest(shipment: Shipment) {
  return {
    ...buildSpoilageRequest(shipment),
    top_n: 10,
  };
}

function getMarketCoordinates(marketName: string): { lat: number; lng: number } | null {
  const market = KENYAN_MARKETS.find((m) => m.name.toLowerCase() === marketName.toLowerCase());
  return market ? { lat: market.latitude, lng: market.longitude } : null;
}

function getDestinationCoordinates(shipment: Shipment): { lat: number; lng: number; name: string } | null {
  const destMarket = KENYAN_MARKETS.find((m) => m.name.toLowerCase() === shipment.destination.toLowerCase());
  if (destMarket) {
    return { lat: destMarket.latitude, lng: destMarket.longitude, name: destMarket.name };
  }
  // Fallback: use stored destination coordinates if available
  if (shipment.destinationLatitude !== undefined && shipment.destinationLongitude !== undefined) {
    return { lat: shipment.destinationLatitude, lng: shipment.destinationLongitude, name: shipment.destination };
  }
  return { lat: -1.2921, lng: 36.8219, name: shipment.destination };
}

const STATUS_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  SCHEDULED: Calendar,
  IN_TRANSIT: Truck,
  DELIVERED: CheckCircle,
  CANCELLED: XCircle,
};

const STATUS_LABELS: Record<string, string> = {
  SCHEDULED: "Scheduled",
  IN_TRANSIT: "In Transit",
  DELIVERED: "Delivered",
  CANCELLED: "Cancelled",
};

const STATUS_COLORS: Record<string, "default" | "secondary" | "warning" | "success" | "destructive"> = {
  SCHEDULED: "secondary",
  IN_TRANSIT: "warning",
  DELIVERED: "success",
  CANCELLED: "destructive",
};

export function ShipmentDetailView({ id }: { id: string }) {
  const router = useRouter();
  const { data: shipment, isLoading, isError, refetch } = useShipment(id);
  const deleteShipment = useDeleteShipment();
  const updateShipment = useUpdateShipment();
  const predictSpoilage = usePredictSpoilage();
  const recommendMarket = useRecommendMarket();

  const [riskData, setRiskData] = useState<{
    spoilage_probability: number;
    risk_tier: "Fresh" | "At-Risk" | "Critical";
    spoil_prediction: boolean;
  } | null>(null);
  const [marketRecommendations, setMarketRecommendations] = useState<MarketRecommendationOut[]>([]);
  const [isPredicting, setIsPredicting] = useState(false);
  const [isRecommending, setIsRecommending] = useState(false);
  const [predictError, setPredictError] = useState(false);
  const [recommendError, setRecommendError] = useState(false);
  const [selectedRoute, setSelectedRoute] = useState<MarketRecommendationOut | null>(null);

  useEffect(() => {
    if (shipment?.marketRecommendations) {
      setMarketRecommendations(shipment.marketRecommendations);
    }
  }, [shipment]);

  async function handlePredict() {
    if (!shipment) return;
    setIsPredicting(true);
    setPredictError(false);
    try {
      const result = await predictSpoilage.mutateAsync(buildSpoilageRequest(shipment));
      setRiskData({
        spoilage_probability: result.spoilage_probability,
        risk_tier: result.risk_tier as "Fresh" | "At-Risk" | "Critical",
        spoil_prediction: result.spoil_prediction,
      });
      await updateShipment.mutateAsync({
        id: shipment.id,
        payload: {
          spoilageProbability: result.spoilage_probability,
          riskTier: result.risk_tier,
          spoilPrediction: result.spoil_prediction,
        },
      });
    } catch {
      setPredictError(true);
    } finally {
      setIsPredicting(false);
    }
  }

  async function handleRecommend() {
    if (!shipment) return;
    setIsRecommending(true);
    setRecommendError(false);
    try {
      const result = await recommendMarket.mutateAsync(buildMarketRequest(shipment));
      setMarketRecommendations(result);
      setSelectedRoute(result[0] ?? null);
      await updateShipment.mutateAsync({
        id: shipment.id,
        payload: { marketRecommendations: result },
      });
    } catch {
      setRecommendError(true);
    } finally {
      setIsRecommending(false);
    }
  }

  async function handleDelete() {
    if (!confirm("Are you sure you want to delete this shipment?")) return;
    try {
      await deleteShipment.mutateAsync(id);
      router.push("/dashboard/shipments");
      router.refresh();
    } catch {
      // Error handled by hook
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Loading..." description="Fetching shipment details" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i}><CardContent className="space-y-3"><Skeleton className="h-4 w-1/4" /><Skeleton className="h-8 w-3/4" /></CardContent></Card>
          ))}
        </div>
      </div>
    );
  }

  if (isError || !shipment) {
    return (
      <div className="space-y-6">
        <PageHeader title="Not found" description="Shipment not found" />
        <ErrorState
          title="Couldn't load shipment"
          description="The shipment may have been removed or you don't have access to it."
          onRetry={() => void refetch()}
        />
      </div>
    );
  }

  const hasMLData = shipment.spoilageProbability !== undefined && shipment.riskTier !== undefined;
  const displayRiskTier = riskData?.risk_tier ?? shipment.riskTier ?? (hasMLData ? getRiskTierFromProbability(shipment.spoilageProbability!) : null);
  const displayProbability = riskData?.spoilage_probability ?? shipment.spoilageProbability;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Shipment Details"
        description={`${shipment.produceType} • ${shipment.origin} → ${shipment.destination}`}
        actions={
          <>
            <Button variant="outline" onClick={() => router.back()}>
              <ArrowLeft className="size-4 mr-2" />
              Back
            </Button>
            <Button variant="destructive" onClick={handleDelete} disabled={deleteShipment.isPending}>
              <Trash2 className="size-4 mr-2" />
              Delete
            </Button>
          </>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {(() => {
                const Icon = STATUS_ICONS[shipment.status] ?? Calendar;
                return <Icon className="size-5 text-muted-foreground" />;
              })()}
              <Badge variant={STATUS_COLORS[shipment.status]}>{STATUS_LABELS[shipment.status]}</Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Scheduled</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Calendar className="size-5 text-muted-foreground" />
              <span>{formatDate(shipment.scheduledDate)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Produce</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Package className="size-5 text-muted-foreground" />
              <span>{shipment.produceType}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Quantity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Scale className="size-5 text-muted-foreground" />
              <span>{shipment.quantityKg ? `${shipment.quantityKg} kg` : "—"}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Separator />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="size-5" />
              Spoilage Risk Prediction
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {hasMLData || riskData ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-lg font-medium">Risk Tier</span>
                  <RiskTierBadge
                    tier={displayRiskTier!}
                    showProbability
                    probability={displayProbability}
                  />
                </div>
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>Spoilage Probability</span>
                  <span className="font-medium">{(displayProbability! * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>Prediction</span>
                  <Badge variant={riskData?.spoil_prediction ?? shipment.spoilPrediction ? "destructive" : "success"}>
                    {riskData?.spoil_prediction ?? shipment.spoilPrediction ? "Will Spoil" : "Will Not Spoil"}
                  </Badge>
                </div>
                <div className="text-xs text-muted-foreground">
                  Threshold: {">15% estimated loss = spoiled. Model ROC-AUC ~0.87 (synthetic data)."}
                </div>
              </div>
            ) : (
              <div className="space-y-3 text-center py-4">
                <p className="text-muted-foreground">No spoilage prediction available for this shipment.</p>
                <Button onClick={handlePredict} disabled={isPredicting} className="w-full">
                  {isPredicting ? (
                    <>
                      <Loader2 className="size-4 mr-2 animate-spin" />
                      Predicting...
                    </>
                  ) : (
                    "Predict Spoilage Risk"
                  )}
                </Button>
                {predictError && (
                  <p className="text-sm text-destructive">Failed to predict. Check that ML service is running.</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="size-5" />
              Market Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {marketRecommendations.length > 0 ? (
              <div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Market</TableHead>
                      <TableHead className="text-right">Distance (km)</TableHead>
                        <TableHead className="text-right">Time</TableHead>
                      <TableHead className="text-right">Price (KES/kg)</TableHead>
                      <TableHead className="text-right">Spoilage %</TableHead>
                      <TableHead className="text-right">Revenue Retained</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {marketRecommendations.map((market, index) => (
                      <TableRow key={market.market_id} className={index === 0 ? "bg-muted/50" : ""}>
                        <TableCell className="font-medium">
                          <div>
                            <span>{market.market_name}</span>
                            <div className="text-xs text-muted-foreground">{market.region}</div>
                          </div>
                        </TableCell>
                        <TableCell className="text-right">{market.distance_km.toFixed(1)}</TableCell>
                        <TableCell className="text-right">
                          {market.duration_minutes !== undefined
                            ? `${(market.duration_minutes / 60).toFixed(1)}h`
                            : "-"}
                        </TableCell>
                        <TableCell className="text-right">{market.price_per_kg.toFixed(2)}</TableCell>
                        <TableCell className="text-right">
                          <Badge variant={(market.spoilage_probability * 100) > 30 ? "destructive" : "default"}>
                            {(market.spoilage_probability * 100).toFixed(1)}%
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right font-medium text-green-600">
                          {market.revenue_retained.toLocaleString()} KES
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                <p className="text-xs text-muted-foreground mt-2">
                  Ranked by revenue retained = quantity × price × (1 − spoilage%). Prices are synthetic-but-calibrated estimates.
                </p>
              </div>
            ) : (
              <div className="space-y-3 text-center py-4">
                <p className="text-muted-foreground">No market recommendations available.</p>
                <Button onClick={handleRecommend} disabled={isRecommending} className="w-full">
                  {isRecommending ? (
                    <>
                      <Loader2 className="size-4 mr-2 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    "Get Market Recommendations"
                  )}
                </Button>
                {recommendError && (
                  <p className="text-sm text-destructive">Failed to load recommendations. Check that ML service is running.</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Map className="size-5" />
            Route & Market Map
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ShipmentMap
            origin={shipment.originLatitude && shipment.originLongitude ? { lat: shipment.originLatitude, lng: shipment.originLongitude, name: shipment.origin } : undefined}
            destination={getDestinationCoordinates(shipment) ?? undefined}
            recommendations={marketRecommendations}
            onRouteClick={setSelectedRoute}
            onShipmentClick={() => setSelectedRoute(marketRecommendations[0] ?? null)}
            showAllMarkets={true}
            height="500px"
          />
          {selectedRoute && (
            <div className="mt-4 rounded-lg border border-border/60 bg-muted/30 p-4 text-sm">
              <div className="flex items-center justify-between gap-3">
                <h3 className="font-semibold">Selected optimized route: {selectedRoute.market_name}</h3>
                <Badge variant="outline">{selectedRoute.route_provider ?? "Estimated route"}</Badge>
              </div>
              <p className="mt-2 text-muted-foreground">
                {selectedRoute.distance_km.toFixed(1)} km · {selectedRoute.duration_minutes !== undefined ? `${(selectedRoute.duration_minutes / 60).toFixed(1)} hours` : "duration unavailable"} · {selectedRoute.price_per_kg.toFixed(2)} KES/kg
              </p>
              <p className="mt-1 text-muted-foreground">Revenue retained: {selectedRoute.revenue_retained.toLocaleString()} KES · Spoilage: {(selectedRoute.spoilage_probability * 100).toFixed(1)}%</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Separator />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Shipment Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <dl className="grid gap-3 sm:grid-cols-2">
              <div>
                <dt className="text-sm text-muted-foreground">Origin</dt>
                <dd className="font-medium">{shipment.origin}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Destination</dt>
                <dd className="font-medium">{shipment.destination}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Created by</dt>
                <dd>{shipment.createdBy}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Created at</dt>
                <dd>{formatDate(shipment.createdAt)}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Updated at</dt>
                <dd>{formatDate(shipment.updatedAt)}</dd>
              </div>
              {shipment.deliveryDate && (
                <div>
                  <dt className="text-sm text-muted-foreground">Delivered at</dt>
                  <dd>{formatDate(shipment.deliveryDate)}</dd>
                </div>
              )}
            </dl>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>ML Prediction Inputs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <dl className="grid gap-3 sm:grid-cols-2">
              <div>
                <dt className="text-sm text-muted-foreground">Origin Latitude</dt>
                <dd>{shipment.originLatitude ?? "Not set"}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Origin Longitude</dt>
                <dd>{shipment.originLongitude ?? "Not set"}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Destination Latitude</dt>
                <dd>{shipment.destinationLatitude ?? "Not set"}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Destination Longitude</dt>
                <dd>{shipment.destinationLongitude ?? "Not set"}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Temperature (°C)</dt>
                <dd>{shipment.temperatureC ?? "Not set"}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Transit Duration (hrs)</dt>
                <dd>{shipment.transitDurationHr ?? "Not set"}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Pressure (PSI)</dt>
                <dd>{shipment.pressurePsi ?? "Not set"}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Baseline Loss (%)</dt>
                <dd>{shipment.baselineLossPct ?? "Not set"}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Quantity (kg)</dt>
                <dd>{shipment.quantityKg ?? "Not set"}</dd>
              </div>
            </dl>
            {!shipment.originLatitude && (
              <p className="text-xs text-muted-foreground">
                Add origin location when creating/editing a shipment to enable spoilage predictions.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}