"use client";

import { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Shipment } from "@/types/shipment.types";
import type { MarketRecommendationOut } from "@/types/ml.types";

interface RevenueByCropDataPoint {
  crop: string;
  revenueRetained: number;
  totalRevenue: number;
  shipmentCount: number;
}

function processRevenueByCropData(
  shipments: Shipment[],
  allRecommendations: Record<string, MarketRecommendationOut[]>
): RevenueByCropDataPoint[] {
  const cropData: Record<string, { revenueRetained: number; totalRevenue: number; count: number }> = {};

  shipments.forEach((shipment) => {
    const recommendations = allRecommendations[shipment.id] ?? [];
    const topMarket = recommendations[0];
    if (topMarket) {
      const crop = shipment.produceType;
      if (!cropData[crop]) {
        cropData[crop] = { revenueRetained: 0, totalRevenue: 0, count: 0 };
      }
      cropData[crop].revenueRetained += topMarket.revenue_retained;
      cropData[crop].totalRevenue += topMarket.revenue_retained / (1 - topMarket.spoilage_probability || 0.01);
      cropData[crop].count += 1;
    }
  });

  return Object.entries(cropData)
    .map(([crop, data]) => ({
      crop,
      revenueRetained: data.revenueRetained,
      totalRevenue: data.totalRevenue,
      shipmentCount: data.count,
    }))
    .sort((a, b) => b.revenueRetained - a.revenueRetained);
}

const COLORS = [
  "hsl(var(--primary))",
  "hsl(var(--secondary))",
  "hsl(var(--accent))",
  "hsl(var(--destructive))",
  "hsl(var(--warning))",
  "hsl(var(--success))",
  "hsl(var(--muted))",
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
];

export function RevenueByCropChart({
  shipments,
  allRecommendations,
}: {
  shipments: Shipment[];
  allRecommendations: Record<string, MarketRecommendationOut[]>;
}) {
  const data = useMemo(
    () => processRevenueByCropData(shipments, allRecommendations),
    [shipments, allRecommendations]
  );

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Revenue Retained by Crop</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            No market recommendation data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Revenue Retained by Crop</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis dataKey="crop" tickLine={false} axisLine={false} />
              <YAxis
                tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
                domain={[0, "auto"]}
              />
              <Tooltip
                formatter={(value) => {
                  const val = (value as number) ?? 0;
                  return [`${val.toLocaleString()} KES`, ""];
                }}
              />
              <Legend />
              <Bar dataKey="revenueRetained" name="Revenue Retained" radius={[4, 4, 0, 0]}>
                {data.map((_, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
              <Bar dataKey="totalRevenue" name="Potential Revenue" radius={[4, 4, 0, 0]} fillOpacity={0.3}>
                {data.map((_, index: number) => (
                  <Cell key={`cell-total-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Solid bars = revenue retained (qty × price × (1−spoilage%)). Outlined = potential revenue if no spoilage.
        </p>
      </CardContent>
    </Card>
  );
}