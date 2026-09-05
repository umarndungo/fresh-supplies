"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  createProduceRequest,
  deleteProduceRequest,
  getProduceRequest,
  listProduceRequest,
  updateProduceRequest,
} from "@/lib/api/produce.api";
import { ApiError } from "@/lib/api/api-error";
import type { CreateProducePayload, UpdateProducePayload } from "@/types/produce.types";

const PRODUCE_QUERY_KEY = ["produce"] as const;

export function useProduce() {
  return useQuery({ queryKey: PRODUCE_QUERY_KEY, queryFn: listProduceRequest });
}

export function useProduceItem(id: string) {
  return useQuery({ queryKey: ["produce", id], queryFn: () => getProduceRequest(id), enabled: !!id });
}

export function useCreateProduce() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateProducePayload) => createProduceRequest(payload),
    onSuccess: () => {
      toast.success("Produce created.");
      void queryClient.invalidateQueries({ queryKey: PRODUCE_QUERY_KEY });
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to create produce.");
    },
  });
}

export function useUpdateProduce() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateProducePayload }) =>
      updateProduceRequest(id, payload),
    onSuccess: () => {
      toast.success("Produce updated.");
      void queryClient.invalidateQueries({ queryKey: PRODUCE_QUERY_KEY });
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to update produce.");
    },
  });
}

export function useDeleteProduce() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteProduceRequest(id),
    onSuccess: () => {
      toast.success("Produce removed.");
      void queryClient.invalidateQueries({ queryKey: PRODUCE_QUERY_KEY });
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to remove produce.");
    },
  });
}