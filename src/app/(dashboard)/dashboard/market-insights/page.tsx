"use client";

import { useState, useMemo } from "react";
import { ArrowUpDown, Filter, DollarSign, BarChart2, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/common/page-header";
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
import { KENYAN_MARKETS, CROP_BASE_PRICE_KES, type Market } from "@/components/map/kenyan-markets";

const CROPS = Object.keys(CROP_BASE_PRICE_KES).sort();

interface MarketPriceRow {
  market: Market;
  prices: Record<string, number>;
}

export default function MarketInsightsPage() {
  const [selectedCrop, setSelectedCrop] = useState<string>("all");
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: "asc" | "desc" }>({ key: "marketName", direction: "asc" });

  // Generate market price data (using base prices + regional variation)
  const marketPriceData = useMemo((): MarketPriceRow[] => {
    return KENYAN_MARKETS.map((market) => {
      const regionMultiplier = getRegionMultiplier(market.region);
      const prices: Record<string, number> = {};
      CROPS.forEach((crop) => {
        const basePrice = CROP_BASE_PRICE_KES[crop] || 50;
        // Add some deterministic variation based on market and crop
        const variation = ((market.latitude + market.longitude) * 1000 + crop.length * 7) % 1;
        prices[crop] = Math.round(basePrice * regionMultiplier * (0.9 + variation * 0.2) * 100) / 100;
      });
      return { market, prices };
    });
  }, []);

  // Filter data based on selected crop
  const displayData = useMemo(() => {
    if (selectedCrop === "all") {
      return marketPriceData.map((row) => ({
        ...row,
        avgPrice: Object.values(row.prices).reduce((a, b) => a + b, 0) / Object.values(row.prices).length,
      }));
    }
    return marketPriceData.map((row) => ({
      ...row,
      avgPrice: row.prices[selectedCrop] ?? 0,
    }));
  }, [marketPriceData, selectedCrop]);

  // Sort data
  const sortedData = useMemo(() => {
    return [...displayData].sort((a, b) => {
      let aVal: string | number;
      let bVal: string | number;

      switch (sortConfig.key) {
        case "marketName":
          aVal = a.market.name;
          bVal = b.market.name;
          break;
        case "region":
          aVal = a.market.region;
          bVal = b.market.region;
          break;
        case "avgPrice":
        default:
          aVal = a.avgPrice;
          bVal = b.avgPrice;
          break;
      }

      if (aVal < bVal) return sortConfig.direction === "asc" ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === "asc" ? 1 : -1;
      return 0;
    });
  }, [displayData, sortConfig]);

  function handleSort(key: string) {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === "asc" ? "desc" : "asc",
    }));
  }

  function getRegionMultiplier(region: string): number {
    const multipliers: Record<string, number> = {
      Nairobi: 1.12,
      Nakuru: 1.0,
      Mombasa: 1.08,
      Kisumu: 0.95,
      Eldoret: 0.98,
      Thika: 1.05,
      Kakamega: 0.92,
      Meru: 0.95,
      Naivasha: 1.02,
      Bomet: 0.9,
    };
    return multipliers[region] ?? 1.0;
  }

  // Chart data for selected crop
  const chartData = useMemo(() => {
    if (selectedCrop === "all") {
      return marketPriceData
        .map((row) => ({
          market: row.market.name,
          avgPrice: Object.values(row.prices).reduce((a, b) => a + b, 0) / Object.values(row.prices).length,
          price: 0,
        }))
        .sort((a, b) => b.avgPrice - a.avgPrice)
        .slice(0, 10);
    }
    return marketPriceData
      .map((row) => ({
        market: row.market.name,
        avgPrice: 0,
        price: row.prices[selectedCrop] ?? 0,
      }))
      .sort((a, b) => b.price - a.price)
      .slice(0, 10);
  }, [marketPriceData, selectedCrop]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Market Insights"
        description="Current calibrated market prices across 10 Kenyan wholesale markets. Prices are synthetic-but-calibrated estimates, not historical trends."
        actions={
          <div className="flex items-center gap-2">
            <Info className="size-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground hidden sm:inline">
              Current calibrated prices, not historical trend
            </span>
          </div>
        }
      />

      <div className="flex flex-wrap gap-3 mb-4">
        <div className="w-[220px]">
          <Select value={selectedCrop} onValueChange={setSelectedCrop}>
            <SelectTrigger>
              <SelectValue placeholder="Select crop" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Crops (Average)</SelectItem>
              {CROPS.map((crop) => (
                <SelectItem key={crop} value={crop}>{crop}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex-1 min-w-[200px]">
          <Input
            placeholder="Search markets..."
            className="max-w-xs"
            onChange={(e) => {
              // Could add search filter here
            }}
          />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="size-5" />
              Market Prices
              {selectedCrop !== "all" && <Badge variant="outline" className="ml-2">{selectedCrop}</Badge>}
              {selectedCrop === "all" && <Badge variant="outline" className="ml-2">Average</Badge>}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead
                      className="cursor-pointer select-none hover:bg-muted"
                      onClick={() => handleSort("marketName")}
                    >
                      <div className="flex items-center gap-1">
                        Market
                        <ArrowUpDown className="size-3" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer select-none hover:bg-muted"
                      onClick={() => handleSort("region")}
                    >
                      <div className="flex items-center gap-1">
                        Region
                        <ArrowUpDown className="size-3" />
                      </div>
                    </TableHead>
                    {selectedCrop === "all" ? (
                      <>
                        {CROPS.map((crop) => (
                          <TableHead
                            key={crop}
                            className="cursor-pointer select-none hover:bg-muted"
                            onClick={() => handleSort(crop)}
                          >
                            <div className="flex items-center gap-1">
                              {crop}
                              <ArrowUpDown className="size-3" />
                            </div>
                          </TableHead>
                        ))}
                      </>
                    ) : (
                      <>
                        <TableHead
                          className="cursor-pointer select-none hover:bg-muted"
                          onClick={() => handleSort("avgPrice")}
                        >
                          <div className="flex items-center gap-1">
                            {selectedCrop}
                            <ArrowUpDown className="size-3" />
                          </div>
                        </TableHead>
                      </>
                    )}
                    <TableHead
                      className="cursor-pointer select-none hover:bg-muted"
                      onClick={() => handleSort("avgPrice")}
                    >
                      <div className="flex items-center gap-1">
                        Avg Price (KES/kg)
                        <ArrowUpDown className="size-3" />
                      </div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedData.map((row) => (
                    <TableRow key={row.market.id}>
                      <TableCell className="font-medium">{row.market.name}</TableCell>
                      <TableCell>{row.market.region}</TableCell>
                      {selectedCrop === "all" ? (
                        <>
                          {CROPS.map((crop) => (
                            <TableCell key={crop} className="text-right font-mono text-sm">
                              {row.prices[crop]?.toFixed(2) ?? "—"}
                            </TableCell>
                          ))}
                        </>
                      ) : (
                        <>
                          <TableCell className="text-right font-mono text-sm">
                            {row.prices[selectedCrop]?.toFixed(2) ?? "—"}
                          </TableCell>
                        </>
                      )}
                      <TableCell className="text-right font-medium">
                        {row.avgPrice?.toFixed(2) ?? "—"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            <p className="text-xs text-muted-foreground mt-3">
              <Info className="size-3 inline mr-1" />
              Prices are synthetic-but-calibrated estimates based on Kenyan wholesale market baselines.
              Regional multipliers applied (e.g., Nairobi +12%, Mombasa +8%). Not historical trend data.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart2 className="size-5" />
              Price Comparison
              {selectedCrop !== "all" && <Badge variant="outline" className="ml-2">{selectedCrop}</Badge>}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} vertical={false} />
                  <XAxis type="number" tickFormatter={(value) => `KES ${value.toFixed(0)}`} />
                  <YAxis
                    type="category"
                    dataKey="market"
                    width={180}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip
                    formatter={(value: any) => [`KES ${(value ?? 0).toFixed(2)}`, "Price per kg"]}
                    labelFormatter={(label: any) => String(label)}
                  />
                  <Legend />
                  <Bar
                    dataKey={selectedCrop === "all" ? "avgPrice" : "price"}
                    name="Price (KES/kg)"
                    radius={[0, 4, 4, 0]}
                    fill="hsl(var(--primary))"
                  >
                    {chartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill="hsl(var(--primary))" />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-muted-foreground mt-3">
              Top 10 markets by {selectedCrop === "all" ? "average price" : `price for ${selectedCrop}`}.
              Current calibrated prices, not historical trend.
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="size-5 text-muted-foreground" />
            Data Source Disclosure
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p><strong>Data Source:</strong> Synthetic-but-calibrated estimates based on Kenyan wholesale market baselines from FAOSTAT and regional market surveys.</p>
            <p><strong>Methodology:</strong> Base prices per crop from CROP_BASE_PRICE_KES, adjusted by regional multipliers (Nairobi +12%, Mombasa +8%, Nakuru baseline, etc.) with deterministic per-market variation.</p>
            <p><strong>Important:</strong> These are <strong>current calibrated price estimates</strong>, <strong>not historical trend data</strong>. Do not interpret as time-series price movements. For trend analysis, historical data integration would be required.</p>
            <p><strong>Last Updated:</strong> Calibrated to 2024 Kenyan wholesale levels. Actual market prices may vary.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}