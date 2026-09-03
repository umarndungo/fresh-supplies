"use client";

import { Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ShipmentStatusBadge } from "@/components/shipments/shipment-status-badge";
import { RoleGate } from "@/components/auth/role-gate";
import { useDeleteShipment } from "@/hooks/use-shipments";
import { formatDate } from "@/lib/utils";
import type { Shipment } from "@/types/shipment.types";

export function ShipmentsTable({ shipments }: { shipments: Shipment[] }) {
  const deleteShipment = useDeleteShipment();

  return (
    <div className="rounded-xl border border-border bg-card">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Origin</TableHead>
            <TableHead>Destination</TableHead>
            <TableHead>Produce</TableHead>
            <TableHead>Scheduled</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {shipments.map((shipment) => (
            <TableRow key={shipment.id}>
              <TableCell className="font-medium text-foreground">{shipment.origin}</TableCell>
              <TableCell>{shipment.destination}</TableCell>
              <TableCell>{shipment.produceType}</TableCell>
              <TableCell>{formatDate(shipment.scheduledDate)}</TableCell>
              <TableCell>
                <ShipmentStatusBadge status={shipment.status} />
              </TableCell>
              <TableCell className="text-right">
                <RoleGate allowed={["ADMINISTRATOR", "LOGISTICS_MANAGER"]}>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Delete shipment"
                    disabled={deleteShipment.isPending}
                    onClick={() => void deleteShipment.mutateAsync(shipment.id)}
                  >
                    <Trash2 className="size-4 text-destructive" />
                  </Button>
                </RoleGate>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
