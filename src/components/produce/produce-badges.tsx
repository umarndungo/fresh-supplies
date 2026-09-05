import { Badge } from "@/components/ui/badge";
import type { ProduceStatus } from "@/types/produce.types";

const STATUS_CONFIG: Record<ProduceStatus, { label: string; variant: "default" | "secondary" | "warning" | "success" | "destructive" }> = {
  AVAILABLE: { label: "Available", variant: "default" },
  RESERVED: { label: "Reserved", variant: "secondary" },
  SOLD: { label: "Sold", variant: "success" },
  SPOILED: { label: "Spoiled", variant: "destructive" },
};

export function ProduceStatusBadge({ status }: { status: ProduceStatus }) {
  const config = STATUS_CONFIG[status];
  return <Badge variant={config.variant}>{config.label}</Badge>;
}

const CLASS_CONFIG: Record<string, { label: string; variant: "default" | "secondary" | "outline" | "destructive" }> = {
  PERISHABLE: { label: "Perishable", variant: "destructive" },
  STAPLE: { label: "Staple", variant: "secondary" },
};

export function CommodityClassBadge({ commodityClass }: { commodityClass: string }) {
  const config = CLASS_CONFIG[commodityClass] ?? { label: commodityClass, variant: "outline" };
  return <Badge variant={config.variant}>{config.label}</Badge>;
}