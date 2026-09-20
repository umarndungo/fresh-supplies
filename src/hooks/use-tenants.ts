"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ApiError } from "@/lib/api/api-error";
import { createTenantRequest, listTenantUsageRequest, listTenantsRequest, updateTenantRequest } from "@/lib/api/admin.api";

export const TENANTS_QUERY_KEY = ["admin", "tenants"] as const;
export const TENANT_USAGE_QUERY_KEY = ["admin", "tenant-usage"] as const;

export function useTenants() {
  return useQuery({ queryKey: TENANTS_QUERY_KEY, queryFn: listTenantsRequest });
}

export function useTenantUsage() {
  return useQuery({ queryKey: TENANT_USAGE_QUERY_KEY, queryFn: listTenantUsageRequest });
}

export function useCreateTenant() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { name: string; adminEmail?: string; adminFullName?: string }) => createTenantRequest(payload),
    onSuccess: () => {
      toast.success("Tenant created.");
      void queryClient.invalidateQueries({ queryKey: TENANTS_QUERY_KEY });
      void queryClient.invalidateQueries({ queryKey: TENANT_USAGE_QUERY_KEY });
    },
    onError: (error) => toast.error(error instanceof ApiError ? error.message : "Unable to create tenant."),
  });
}

export function useUpdateTenant() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, name }: { id: string; name: string }) => updateTenantRequest(id, { name }),
    onSuccess: () => {
      toast.success("Tenant renamed.");
      void queryClient.invalidateQueries({ queryKey: TENANTS_QUERY_KEY });
    },
    onError: (error) => toast.error(error instanceof ApiError ? error.message : "Unable to rename tenant."),
  });
}