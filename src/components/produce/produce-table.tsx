"use client";

import { Trash2, Edit2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { RoleGate } from "@/components/auth/role-gate";
import { useDeleteProduce } from "@/hooks/use-produce";
import { formatDate } from "@/lib/utils";
import { ProduceStatusBadge, CommodityClassBadge } from "@/components/produce/produce-badges";
import type { Produce } from "@/types/produce.types";

export function ProduceTable({ produceList }: { produceList: Produce[] }) {
  const deleteProduce = useDeleteProduce();

  return (
    <div className="rounded-xl border border-border bg-card">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Variety</TableHead>
            <TableHead>Class</TableHead>
            <TableHead>Quantity (kg)</TableHead>
            <TableHead>Price (KES/kg)</TableHead>
            <TableHead>Grade</TableHead>
            <TableHead>Harvested</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {produceList.map((item) => (
            <TableRow key={item.id}>
              <TableCell className="font-medium text-foreground">{item.name}</TableCell>
              <TableCell>{item.variety}</TableCell>
              <TableCell><CommodityClassBadge commodityClass={item.commodityClass} /></TableCell>
              <TableCell className="text-right">{item.quantityKg.toLocaleString()}</TableCell>
              <TableCell className="text-right">{item.unitPrice.toLocaleString()}</TableCell>
              <TableCell>{item.qualityGrade}</TableCell>
              <TableCell>{formatDate(item.harvestDate)}</TableCell>
              <TableCell><ProduceStatusBadge status={item.status} /></TableCell>
              <TableCell className="text-right">
                <RoleGate allowed={["ADMINISTRATOR", "LOGISTICS_MANAGER", "FARMER_COOPERATIVE"]}>
                  <Button variant="ghost" size="icon" aria-label="Edit produce" disabled={false}>
                    <Edit2 className="size-4" />
                  </Button>
                </RoleGate>
                <RoleGate allowed={["ADMINISTRATOR", "LOGISTICS_MANAGER"]}>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Delete produce"
                    disabled={deleteProduce.isPending}
                    onClick={() => void deleteProduce.mutateAsync(item.id)}
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