"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  createShipmentRequest,
  deleteShipmentRequest,
  listShipmentsRequest,
  updateShipmentRequest,
} from "@/lib/api/shipment.api";
import { ApiError } from "@/lib/api/api-error";
import type { CreateShipmentPayload, UpdateShipmentPayload } from "@/types/shipment.types";

const SHIPMENTS_QUERY_KEY = ["shipments"] as const;

export function useShipments() {
  return useQuery({ queryKey: SHIPMENTS_QUERY_KEY, queryFn: listShipmentsRequest });
}

export function useCreateShipment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateShipmentPayload) => createShipmentRequest(payload),
    onSuccess: () => {
      toast.success("Shipment created.");
      void queryClient.invalidateQueries({ queryKey: SHIPMENTS_QUERY_KEY });
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to create shipment.");
    },
  });
}

export function useUpdateShipment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateShipmentPayload }) =>
      updateShipmentRequest(id, payload),
    onSuccess: () => {
      toast.success("Shipment updated.");
      void queryClient.invalidateQueries({ queryKey: SHIPMENTS_QUERY_KEY });
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to update shipment.");
    },
  });
}

export function useDeleteShipment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteShipmentRequest(id),
    onSuccess: () => {
      toast.success("Shipment removed.");
      void queryClient.invalidateQueries({ queryKey: SHIPMENTS_QUERY_KEY });
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to remove shipment.");
    },
  });
}
