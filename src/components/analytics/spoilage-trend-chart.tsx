"use client";

import { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Shipment } from "@/types/shipment.types";

interface SpoilageTrendDataPoint {
  date: string;
  avgSpoilageProbability: number;
  shipmentCount: number;
}

function processSpoilageTrendData(shipments: Shipment[]): SpoilageTrendDataPoint[] {
  const monthlyData: Record<string, { sum: number; count: number }> = {};

  shipments.forEach((shipment) => {
    if (shipment.spoilageProbability !== undefined) {
      const date = new Date(shipment.scheduledDate);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
      if (!monthlyData[monthKey]) {
        monthlyData[monthKey] = { sum: 0, count: 0 };
      }
      monthlyData[monthKey].sum += shipment.spoilageProbability;
      monthlyData[monthKey].count += 1;
    }
  });

  return Object.entries(monthlyData)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([month, data]) => ({
      date: month,
      avgSpoilageProbability: data.sum / data.count,
      shipmentCount: data.count,
    }));
}

export function SpoilageTrendChart({ shipments }: { shipments: Shipment[] }) {
  const data = useMemo(() => processSpoilageTrendData(shipments), [shipments]);

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Spoilage Trend Over Time</CardTitle>
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
        <CardTitle>Spoilage Trend Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis
                dataKey="date"
                tickFormatter={(value) => {
                  const [year, month] = value.split("-");
                  return `${month}/${year.slice(2)}`;
                }}
              />
              <YAxis
                tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                domain={[0, "auto"]}
              />
              <Tooltip
                formatter={(value) => {
                  const val = (value as number) ?? 0;
                  return [`${(val * 100).toFixed(1)}%`, "Avg Spoilage Probability"];
                }}
                labelFormatter={(value) => {
                  const str = String(value);
                  const [year, month] = str.split("-");
                  return `${month}/${year}`;
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="avgSpoilageProbability"
                name="Avg Spoilage Probability"
                stroke="hsl(var(--destructive))"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Based on shipments with ML predictions. Threshold: {">15% = spoiled"}.
        </p>
      </CardContent>
    </Card>
  );
}