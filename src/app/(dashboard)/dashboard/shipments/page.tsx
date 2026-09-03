"use client";

import { Truck } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { EmptyState } from "@/components/common/empty-state";
import { ErrorState } from "@/components/common/error-state";
import { DashboardSkeleton } from "@/components/common/dashboard-skeleton";
import { RoleGate } from "@/components/auth/role-gate";
import { CreateShipmentDialog } from "@/components/shipments/create-shipment-dialog";
import { ShipmentsTable } from "@/components/shipments/shipments-table";
import { useShipments } from "@/hooks/use-shipments";

export default function ShipmentsPage() {
  const { data: shipments, isLoading, isError, refetch } = useShipments();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Shipments"
        description="Track produce moving from cooperatives to market."
        actions={
          <RoleGate allowed={["ADMINISTRATOR", "LOGISTICS_MANAGER"]}>
            <CreateShipmentDialog />
          </RoleGate>
        }
      />
      {isLoading ? (
        <DashboardSkeleton />
      ) : isError ? (
        <ErrorState
          title="Couldn't load shipments"
          description="Check your connection and try again."
          onRetry={() => void refetch()}
        />
      ) : shipments && shipments.length > 0 ? (
        <ShipmentsTable shipments={shipments} />
      ) : (
        <EmptyState icon={Truck} title="No shipments yet" description="Scheduled shipments will show up here." />
      )}
    </div>
  );
}
