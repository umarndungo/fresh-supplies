"use client";

import { RefreshCw, BarChart2, PieChart, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/common/page-header";
import { RoleGate } from "@/components/auth/role-gate";
import { useShipments } from "@/hooks/use-shipments";
import { useAllMarketRecommendations } from "@/hooks/use-analytics";
import { SpoilageTrendChart } from "@/components/analytics/spoilage-trend-chart";
import { RevenueByCropChart } from "@/components/analytics/revenue-by-crop-chart";
import { RiskDistributionChart } from "@/components/analytics/risk-distribution-chart";
import { DashboardSkeleton } from "@/components/common/dashboard-skeleton";
import { ErrorState } from "@/components/common/error-state";
import type { Shipment } from "@/types/shipment.types";

export default function AnalyticsPage() {
  const { data: shipments, isLoading, isError, refetch } = useShipments();
  const { data: allRecommendations, isLoading: isRecLoading } = useAllMarketRecommendations(shipments ?? []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Analytics" description="Spoilage trends, revenue analysis, and risk distribution" />
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i}><CardContent className="h-64"><DashboardSkeleton /></CardContent></Card>
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="space-y-6">
        <PageHeader title="Analytics" description="Spoilage trends, revenue analysis, and risk distribution" />
        <ErrorState
          title="Couldn't load shipments"
          description="Check your connection and try again."
          onRetry={() => void refetch()}
        />
      </div>
    );
  }

  const shipmentsWithPredictions = (shipments ?? []).filter(
    (s) => s.spoilageProbability !== undefined || s.riskTier !== undefined
  );

  const totalShipments = shipments?.length ?? 0;
  const withPredictions = shipmentsWithPredictions.length;
  const avgSpoilage = withPredictions > 0
    ? shipmentsWithPredictions.reduce((sum, s) => sum + (s.spoilageProbability ?? 0), 0) / withPredictions
    : 0;

  const riskCounts = shipmentsWithPredictions.reduce(
    (acc, s) => {
      let tier: "Fresh" | "At-Risk" | "Critical" | null = null;
      if (s.riskTier) tier = s.riskTier;
      else if (s.spoilageProbability !== undefined) {
        if (s.spoilageProbability < 0.33) tier = "Fresh";
        else if (s.spoilageProbability < 0.66) tier = "At-Risk";
        else tier = "Critical";
      }
      if (tier) acc[tier] += 1;
      return acc;
    },
    { Fresh: 0, "At-Risk": 0, Critical: 0 } as { Fresh: number; "At-Risk": number; Critical: number }
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analytics"
        description="Spoilage trends, revenue analysis, and risk distribution"
        actions={
          <button onClick={() => void refetch()} disabled={isRecLoading} className="btn btn-outline btn-sm">
            <RefreshCw className={`size-4 mr-2 ${isRecLoading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Shipments</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalShipments}</div>
            <p className="text-xs text-muted-foreground">{withPredictions} with ML predictions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Spoilage Risk</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{(avgSpoilage * 100).toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">Threshold: {">15% = spoiled"}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">At-Risk Shipments</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-warning">{riskCounts["At-Risk"] + riskCounts.Critical}</div>
            <p className="text-xs text-muted-foreground">At-Risk + Critical tiers</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Critical Shipments</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{riskCounts.Critical}</div>
            <p className="text-xs text-muted-foreground">Immediate attention needed</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <SpoilageTrendChart shipments={shipments ?? []} />
        <RevenueByCropChart shipments={shipments ?? []} allRecommendations={allRecommendations ?? {}} />
      </div>

      <RiskDistributionChart shipments={shipments ?? []} />

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart2 className="size-5" />
              Quick Stats
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <dl className="grid gap-2 sm:grid-cols-2">
              <div>
                <dt className="text-sm text-muted-foreground">Fresh</dt>
                <dd className="font-medium text-success">{riskCounts.Fresh}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">At-Risk</dt>
                <dd className="font-medium text-warning">{riskCounts["At-Risk"]}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">Critical</dt>
                <dd className="font-medium text-destructive">{riskCounts.Critical}</dd>
              </div>
              <div>
                <dt className="text-sm text-muted-foreground">No Prediction</dt>
                <dd className="font-medium text-muted-foreground">{totalShipments - withPredictions}</dd>
              </div>
            </dl>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="size-5" />
              Risk Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {withPredictions > 0 ? (
              <>
                <div className="flex items-center justify-between text-sm">
                  <span>Fresh</span>
                  <span className="font-medium">{((riskCounts.Fresh / withPredictions) * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span>At-Risk</span>
                  <span className="font-medium">{((riskCounts["At-Risk"] / withPredictions) * 100).toFixed(1)}%</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span>Critical</span>
                  <span className="font-medium">{((riskCounts.Critical / withPredictions) * 100).toFixed(1)}%</span>
                </div>
              </>
            ) : (
              <p className="text-muted-foreground text-sm">No prediction data</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="size-5" />
              Data Coverage
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Shipments with Predictions</span>
              <span className="font-medium">{withPredictions} / {totalShipments}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Coverage</span>
              <span className="font-medium">
                {totalShipments > 0 ? ((withPredictions / totalShipments) * 100).toFixed(1) : 0}%
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>ML Model</span>
              <span className="font-medium">XGBoost (ROC-AUC ~0.87)</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Data Source</span>
              <span className="font-medium">Synthetic (calibrated)</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}