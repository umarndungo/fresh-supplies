"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  createAdminUserRequest,
  deleteAdminUserRequest,
  listAdminUsersRequest,
  updateAdminUserRequest,
} from "@/lib/api/admin.api";
import { ApiError } from "@/lib/api/api-error";
import type { CreateAdminUserPayload, UpdateAdminUserPayload } from "@/types/admin.types";

const ADMIN_USERS_QUERY_KEY = ["admin", "users"] as const;

export function useAdminUsers() {
  return useQuery({ queryKey: ADMIN_USERS_QUERY_KEY, queryFn: listAdminUsersRequest });
}

export function useCreateAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateAdminUserPayload) => createAdminUserRequest(payload),
    onSuccess: () => {
      toast.success("User invited.");
      void queryClient.invalidateQueries({ queryKey: ADMIN_USERS_QUERY_KEY });
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to invite user.");
    },
  });
}

export function useUpdateAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateAdminUserPayload }) =>
      updateAdminUserRequest(id, payload),
    onSuccess: () => {
      toast.success("User updated.");
      void queryClient.invalidateQueries({ queryKey: ADMIN_USERS_QUERY_KEY });
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to update user.");
    },
  });
}

export function useDeleteAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteAdminUserRequest(id),
    onSuccess: () => {
      toast.success("User removed.");
      void queryClient.invalidateQueries({ queryKey: ADMIN_USERS_QUERY_KEY });
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to remove user.");
    },
  });
}