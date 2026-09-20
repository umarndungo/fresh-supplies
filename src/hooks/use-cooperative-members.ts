"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { createCooperativeMemberRequest, listCooperativeMembersRequest } from "@/lib/api/admin.api";
import { ApiError } from "@/lib/api/api-error";

const COOPERATIVE_MEMBERS_QUERY_KEY = ["cooperative", "members"] as const;

export function useCooperativeMembers() {
  return useQuery({ queryKey: COOPERATIVE_MEMBERS_QUERY_KEY, queryFn: listCooperativeMembersRequest });
}

export function useCreateCooperativeMember() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { fullName: string; email: string; role: "FARMER_COOPERATIVE" | "DRIVER" }) =>
      createCooperativeMemberRequest(payload),
    onSuccess: () => {
      toast.success("Invited — they'll get an email with sign-in instructions.");
      void queryClient.invalidateQueries({ queryKey: COOPERATIVE_MEMBERS_QUERY_KEY });
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to add them.");
    },
  });
}
