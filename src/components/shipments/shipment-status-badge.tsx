import { Badge } from "@/components/ui/badge";
import type { ShipmentStatus } from "@/types/shipment.types";

const STATUS_CONFIG: Record<ShipmentStatus, { label: string; variant: "secondary" | "warning" | "success" | "destructive" }> = {
  SCHEDULED: { label: "Scheduled", variant: "secondary" },
  IN_TRANSIT: { label: "In transit", variant: "warning" },
  DELIVERED: { label: "Delivered", variant: "success" },
  CANCELLED: { label: "Cancelled", variant: "destructive" },
};

export function ShipmentStatusBadge({ status }: { status: ShipmentStatus }) {
  const config = STATUS_CONFIG[status];
  return <Badge variant={config.variant}>{config.label}</Badge>;
}
