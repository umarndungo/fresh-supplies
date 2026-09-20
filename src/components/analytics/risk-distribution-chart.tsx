"use client";

import { useMemo } from "react";
import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LabelList,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Shipment } from "@/types/shipment.types";
import { getRiskTierFromProbability } from "@/components/shipments/risk-tier-badge";

interface RiskDistributionDataPoint {
  tier: "Fresh" | "At-Risk" | "Critical";
  count: number;
  percentage: number;
}

const TIER_COLORS: Record<string, string> = {
  Fresh: "hsl(var(--success))",
  "At-Risk": "hsl(var(--warning))",
  Critical: "hsl(var(--destructive))",
};

const TIER_LABELS: Record<string, string> = {
  Fresh: "Fresh (<33%)",
  "At-Risk": "At-Risk (33-66%)",
  Critical: "Critical (>66%)",
};

function processRiskDistributionData(shipments: Shipment[]): RiskDistributionDataPoint[] {
  const tierCounts: Record<string, number> = {
    Fresh: 0,
    "At-Risk": 0,
    Critical: 0,
  };

  let totalWithPrediction = 0;

  shipments.forEach((shipment) => {
    let tier: "Fresh" | "At-Risk" | "Critical" | null = null;

    if (shipment.riskTier) {
      tier = shipment.riskTier;
    } else if (shipment.spoilageProbability !== undefined) {
      tier = getRiskTierFromProbability(shipment.spoilageProbability);
    }

    if (tier && (tier === "Fresh" || tier === "At-Risk" || tier === "Critical")) {
      tierCounts[tier] = (tierCounts[tier] ?? 0) + 1;
      totalWithPrediction += 1;
    }
  });

  return (["Fresh", "At-Risk", "Critical"] as const).map((tier) => ({
    tier,
    count: tierCounts[tier] ?? 0,
    percentage: totalWithPrediction > 0 ? ((tierCounts[tier] ?? 0) / totalWithPrediction) * 100 : 0,
  }));
}

export function RiskDistributionChart({ shipments }: { shipments: Shipment[] }) {
  const data = useMemo(() => processRiskDistributionData(shipments), [shipments]);
  const totalWithPrediction = data.reduce((sum: number, d) => sum + (d.count ?? 0), 0);

  if (totalWithPrediction === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Risk Tier Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            No spoilage prediction data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Risk Tier Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              layout="vertical"
              margin={{ top: 5, right: 70, left: 8, bottom: 5 }}
              barCategoryGap="30%"
            >
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} horizontal={false} />
              <XAxis type="number" allowDecimals={false} />
              <YAxis
                type="category"
                dataKey="tier"
                width={110}
                tickFormatter={(tier: string) => TIER_LABELS[tier] ?? tier}
              />
              <Tooltip
                formatter={(value, _name, item) => {
                  const val = (value as number) ?? 0;
                  const pct = (item?.payload as RiskDistributionDataPoint | undefined)?.percentage ?? 0;
                  return [`${val} shipments (${pct.toFixed(1)}%)`, "Count"];
                }}
                labelFormatter={(tier) => TIER_LABELS[String(tier)] ?? String(tier)}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {data.map((entry, index: number) => (
                  <Cell key={`cell-${index}`} fill={TIER_COLORS[entry.tier]} />
                ))}
                <LabelList
                  position="right"
                  valueAccessor={(entry) => {
                    const payload = entry.payload as RiskDistributionDataPoint;
                    return `${payload.count} (${payload.percentage.toFixed(1)}%)`;
                  }}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          {totalWithPrediction} of {shipments.length} shipments have predictions. Threshold: {">15% = spoiled"}.
        </p>
      </CardContent>
    </Card>
  );
}