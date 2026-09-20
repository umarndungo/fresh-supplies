"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ApiError } from "@/lib/api/api-error";
import { createGrantRequest, listGrantsForTenantRequest, revokeGrantRequest } from "@/lib/api/admin.api";
import type { CreateGrantPayload } from "@/types/tenant.types";

export function useTenantGrants(tenantId: string | undefined) {
  return useQuery({
    queryKey: ["admin", "grants", tenantId],
    queryFn: () => listGrantsForTenantRequest(tenantId!),
    enabled: Boolean(tenantId),
  });
}

export function useCreateGrant() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateGrantPayload) => createGrantRequest(payload),
    onSuccess: (_, payload) => {
      toast.success("Access grant created.");
      void queryClient.invalidateQueries({ queryKey: ["admin", "grants", payload.cooperativeId] });
    },
    onError: (error) => toast.error(error instanceof ApiError ? error.message : "Unable to create access grant."),
  });
}

export function useRevokeGrant() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id }: { id: string; cooperativeId: string }) => revokeGrantRequest(id),
    onSuccess: (_, variables) => {
      toast.success("Access grant revoked.");
      void queryClient.invalidateQueries({ queryKey: ["admin", "grants", variables.cooperativeId] });
    },
    onError: (error) => toast.error(error instanceof ApiError ? error.message : "Unable to revoke access grant."),
  });
}