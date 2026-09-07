"use client";

import { useState, useCallback, useMemo } from "react";
import { Download, FileText, Filter, Calendar, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/common/page-header";
import { DashboardSkeleton } from "@/components/common/dashboard-skeleton";
import { useShipments } from "@/hooks/use-shipments";
import { useProduce } from "@/hooks/use-produce";
import { useAllMarketRecommendations } from "@/hooks/use-analytics";
import { formatDate } from "@/lib/utils";
import type { Shipment } from "@/types/shipment.types";
import type { Produce } from "@/types/produce.types";

type ReportType = "shipments" | "produce" | "analytics";

const REPORT_TYPES: { value: ReportType; label: string; description: string }[] = [
  { value: "shipments", label: "Shipments", description: "All shipment records with ML predictions" },
  { value: "produce", label: "Produce Inventory", description: "Current produce stock across cooperatives" },
  { value: "analytics", label: "Analytics Summary", description: "Risk distribution, revenue, and spoilage trends" },
];

function generateCSV(data: any[], headers: string[]): string {
  const rows = [
    headers.join(","),
    ...data.map((row) => headers.map((h) => `"${String(row[h] ?? "").replace(/"/g, '""')}"`).join(",")),
  ];
  return rows.join("\n");
}

function downloadCSV(csv: string, filename: string) {
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

function formatStatus(status: string): string {
  return status.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function ReportsPage() {
  const { data: shipments, isLoading: shipmentsLoading } = useShipments();
  const { data: produce, isLoading: produceLoading } = useProduce();
  const { data: allRecommendations, isLoading: recLoading } = useAllMarketRecommendations([]);

  const [reportType, setReportType] = useState<ReportType>("shipments");
  const [dateRange, setDateRange] = useState<{ from: string; to: string }>({ from: "", to: "" });
  const [isExporting, setIsExporting] = useState(false);

  const shipmentsWithRecs = (shipments ?? []).map((s) => ({
    ...s,
    recommendations: [],
  }));

  const handleExport = useCallback(async () => {
    setIsExporting(true);
    try {
      let csv = "";
      let filename = "";
      const now = new Date().toISOString().split("T")[0];

      switch (reportType) {
        case "shipments": {
          const data = (shipments ?? []).map((s: Shipment) => ({
            ID: s.id,
            Origin: s.origin,
            Destination: s.destination,
            Produce: s.produceType,
            Status: formatStatus(s.status),
            "Scheduled Date": formatDate(s.scheduledDate),
            "Delivery Date": s.deliveryDate ? formatDate(s.deliveryDate) : "",
            "Risk Tier": s.riskTier ?? "",
            "Spoilage Probability": s.spoilageProbability !== undefined ? (s.spoilageProbability * 100).toFixed(1) + "%" : "",
            "Latitude": s.originLatitude ?? "",
            "Longitude": s.originLongitude ?? "",
            "Temperature (°C)": s.temperatureC ?? "",
            "Transit Duration (hrs)": s.transitDurationHr ?? "",
            "Pressure (PSI)": s.pressurePsi ?? "",
            "Baseline Loss (%)": s.baselineLossPct ?? "",
            "Quantity (kg)": s.quantityKg ?? "",
            "Created By": s.createdBy,
            "Created At": formatDate(s.createdAt),
            "Updated At": formatDate(s.updatedAt),
          }));
          csv = generateCSV(data, [
            "ID", "Origin", "Destination", "Produce", "Status", "Scheduled Date", "Delivery Date",
            "Risk Tier", "Spoilage Probability", "Latitude", "Longitude", "Temperature (°C)",
            "Transit Duration (hrs)", "Pressure (PSI)", "Baseline Loss (%)", "Quantity (kg)",
            "Created By", "Created At", "Updated At"
          ]);
          filename = `shipments-report-${now}.csv`;
          break;
        }
        case "produce": {
          const data = (produce ?? []).map((p: Produce) => ({
            ID: p.id,
            Name: p.name,
            Variety: p.variety,
            "Commodity Class": p.commodityClass,
            "Quantity (kg)": p.quantityKg,
            "Unit Price (KES/kg)": p.unitPrice,
            "Quality Grade": p.qualityGrade,
            "Harvest Date": formatDate(p.harvestDate),
            "Storage Location": p.storageLocation,
            Status: formatStatus(p.status),
            "Cooperative ID": p.cooperativeId,
            "Created At": formatDate(p.createdAt),
            "Updated At": formatDate(p.updatedAt),
          }));
          csv = generateCSV(data, [
            "ID", "Name", "Variety", "Commodity Class", "Quantity (kg)", "Unit Price (KES/kg)",
            "Quality Grade", "Harvest Date", "Storage Location", "Status", "Cooperative ID",
            "Created At", "Updated At"
          ]);
          filename = `produce-report-${now}.csv`;
          break;
        }
        case "analytics": {
          const shipmentsData = shipments ?? [];
          const withPredictions = shipmentsData.filter((s) => s.spoilageProbability !== undefined);
          const riskCounts = withPredictions.reduce((acc, s) => {
            const tier = s.riskTier ?? (s.spoilageProbability !== undefined
              ? (s.spoilageProbability < 0.33 ? "Fresh" : s.spoilageProbability < 0.66 ? "At-Risk" : "Critical")
              : "Unknown");
            acc[tier] = (acc[tier] ?? 0) + 1;
            return acc;
          }, {} as Record<string, number>);

          const avgSpoilage = withPredictions.length > 0
            ? withPredictions.reduce((sum, s) => sum + (s.spoilageProbability ?? 0), 0) / withPredictions.length
            : 0;

          const data = [
            { Metric: "Total Shipments", Value: shipmentsData.length },
            { Metric: "Shipments with ML Predictions", Value: withPredictions.length },
            { Metric: "Average Spoilage Risk (%)", Value: (avgSpoilage * 100).toFixed(1) },
            { Metric: "Fresh", Value: riskCounts.Fresh ?? 0 },
            { Metric: "At-Risk", Value: riskCounts["At-Risk"] ?? 0 },
            { Metric: "Critical", Value: riskCounts.Critical ?? 0 },
            { Metric: "Coverage (%)", Value: shipmentsData.length > 0 ? ((withPredictions.length / shipmentsData.length) * 100).toFixed(1) : "0" },
          ];
          csv = generateCSV(data, ["Metric", "Value"]);
          filename = `analytics-report-${now}.csv`;
          break;
        }
      }

      downloadCSV(csv, filename);
      setIsExporting(false);
    } catch (error) {
      console.error("Export failed:", error);
      setIsExporting(false);
    }
  }, [reportType, shipments, produce, formatDate]);

  // Filter shipments by date range
  const filteredShipments = useMemo(() => {
    if (!dateRange.from && !dateRange.to) return shipments ?? [];
    return (shipments ?? []).filter((s) => {
      const scheduled = new Date(s.scheduledDate);
      if (dateRange.from && scheduled < new Date(dateRange.from)) return false;
      if (dateRange.to && scheduled > new Date(dateRange.to)) return false;
      return true;
    });
  }, [shipments, dateRange]);

  const filteredProduce = useMemo(() => {
    if (!dateRange.from && !dateRange.to) return produce ?? [];
    return (produce ?? []).filter((p) => {
      const harvest = new Date(p.harvestDate);
      if (dateRange.from && harvest < new Date(dateRange.from)) return false;
      if (dateRange.to && harvest > new Date(dateRange.to)) return false;
      return true;
    });
  }, [produce, dateRange]);

  const loading = shipmentsLoading || produceLoading || recLoading;

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Reports" description="Export data reports as CSV" />
        <Card><CardContent className="h-64 flex items-center justify-center text-muted-foreground">Loading data...</CardContent></Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Reports"
        description="Export data reports as CSV. Select report type, apply date filters, and download."
      />

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="size-5" />
            Report Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <label className="block text-sm font-medium mb-1">Report Type</label>
              <Select value={reportType} onValueChange={(v) => setReportType(v as ReportType)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select report type" />
                </SelectTrigger>
                <SelectContent>
                  {REPORT_TYPES.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground mt-1">
                {REPORT_TYPES.find((t) => t.value === reportType)?.description}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Date Range (Optional)</label>
              <div className="flex gap-2">
                <Input
                  type="date"
                  value={dateRange.from}
                  onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
                  placeholder="From"
                />
                <Input
                  type="date"
                  value={dateRange.to}
                  onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
                  placeholder="To"
                />
              </div>
            </div>

            <div className="flex items-end">
              <Button onClick={handleExport} disabled={isExporting} className="w-full" size="lg">
                {isExporting ? (
                  <>
                    <Download className="size-4 mr-2 animate-spin" />
                    Generating CSV...
                  </>
                ) : (
                  <>
                    <Download className="size-4 mr-2" />
                    Export CSV
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="size-5" />
            Preview: {REPORT_TYPES.find((t) => t.value === reportType)?.label}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            {reportType === "shipments" && (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Origin</TableHead>
                    <TableHead>Destination</TableHead>
                    <TableHead>Produce</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Risk Tier</TableHead>
                    <TableHead>Scheduled</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(filteredShipments ?? []).slice(0, 20).map((s) => (
                    <TableRow key={s.id}>
                      <TableCell className="font-mono text-xs">{s.id.slice(0, 8)}...</TableCell>
                      <TableCell>{s.origin}</TableCell>
                      <TableCell>{s.destination}</TableCell>
                      <TableCell>{s.produceType}</TableCell>
                      <TableCell><Badge variant={s.status === "IN_TRANSIT" ? "default" : "secondary"}>{formatStatus(s.status)}</Badge></TableCell>
                      <TableCell><Badge variant={s.riskTier === "Critical" ? "destructive" : s.riskTier === "At-Risk" ? "warning" : "default"}>{s.riskTier ?? "—"}</Badge></TableCell>
                      <TableCell>{formatDate(s.scheduledDate)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}

            {reportType === "produce" && (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Variety</TableHead>
                    <TableHead>Class</TableHead>
                    <TableHead>Qty (kg)</TableHead>
                    <TableHead>Price (KES/kg)</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(filteredProduce ?? []).slice(0, 20).map((p) => (
                    <TableRow key={p.id}>
                      <TableCell className="font-mono text-xs">{p.id.slice(0, 8)}...</TableCell>
                      <TableCell>{p.name}</TableCell>
                      <TableCell>{p.variety}</TableCell>
                      <TableCell><Badge variant={p.commodityClass === "PERISHABLE" ? "destructive" : "secondary"}>{p.commodityClass}</Badge></TableCell>
                      <TableCell className="text-right">{p.quantityKg.toLocaleString()}</TableCell>
                      <TableCell className="text-right">{p.unitPrice.toLocaleString()}</TableCell>
                      <TableCell><Badge variant={p.status === "AVAILABLE" ? "default" : p.status === "SOLD" ? "success" : "destructive"}>{formatStatus(p.status)}</Badge></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}

            {reportType === "analytics" && (
              <div className="grid gap-4 md:grid-cols-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Total Shipments</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{(shipments ?? []).length}</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">With Predictions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-primary">
                      {(shipments ?? []).filter((s) => s.spoilageProbability !== undefined).length}
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Avg Spoilage Risk</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-destructive">
                      {((shipments ?? []).filter((s) => s.spoilageProbability !== undefined).reduce((sum, s) => sum + (s.spoilageProbability ?? 0), 0) /
                        Math.max(1, (shipments ?? []).filter((s) => s.spoilageProbability !== undefined).length) * 100).toFixed(1)}%
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Coverage</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {(shipments ?? []).length > 0
                        ? (((shipments ?? []).filter((s) => s.spoilageProbability !== undefined).length / (shipments ?? []).length) * 100).toFixed(1) + "%"
                        : "0%"}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
          <p className="text-xs text-muted-foreground mt-3">Showing first 20 records. Full dataset will be exported to CSV.</p>
        </CardContent>
      </Card>
    </div>
  );
}