"use client";

import { Package } from "lucide-react";
import { PageHeader } from "@/components/common/page-header";
import { EmptyState } from "@/components/common/empty-state";
import { ErrorState } from "@/components/common/error-state";
import { DashboardSkeleton } from "@/components/common/dashboard-skeleton";
import { RoleGate } from "@/components/auth/role-gate";
import { CreateProduceDialog } from "@/components/produce/create-produce-dialog";
import { ProduceTable } from "@/components/produce/produce-table";
import { useProduce } from "@/hooks/use-produce";

export default function ProducePage() {
  const { data: produce, isLoading, isError, refetch } = useProduce();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Produce Inventory"
        description="Track produce stock across cooperatives."
        actions={
          <RoleGate allowed={["ADMINISTRATOR", "LOGISTICS_MANAGER", "FARMER_COOPERATIVE"]}>
            <CreateProduceDialog />
          </RoleGate>
        }
      />
      {isLoading ? (
        <DashboardSkeleton />
      ) : isError ? (
        <ErrorState
          title="Couldn't load produce"
          description="Check your connection and try again."
          onRetry={() => void refetch()}
        />
      ) : produce && produce.length > 0 ? (
        <ProduceTable produceList={produce} />
      ) : (
        <EmptyState icon={Package} title="No produce yet" description="Produce inventory will show up here." />
      )}
    </div>
  );
}