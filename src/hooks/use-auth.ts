"use client";

import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuthContext } from "@/context/auth-context";
import { ApiError } from "@/lib/api/api-error";
import { ROUTES } from "@/lib/constants";
import type { LoginCredentials, RegisterPayload } from "@/types/auth.types";

export function useAuth() {
  const { user, status, login, register, logout } = useAuthContext();
  const router = useRouter();

  const loginMutation = useMutation({
    mutationFn: (credentials: LoginCredentials) => login(credentials),
    onSuccess: (authUser) => {
      toast.success(`Welcome back, ${authUser.fullName.split(" ")[0]}.`);
      router.push(ROUTES.dashboard);
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to sign in. Please try again.");
    },
  });

  const registerMutation = useMutation({
    mutationFn: (payload: RegisterPayload) => register(payload),
    onSuccess: (authUser) => {
      toast.success(`Account created. Welcome, ${authUser.fullName.split(" ")[0]}.`);
      router.push(ROUTES.dashboard);
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to create your account.");
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => logout(),
    onSuccess: () => {
      toast.success("You have been signed out.");
      router.push(ROUTES.login);
    },
    onError: () => {
      router.push(ROUTES.login);
    },
  });

  return {
    user,
    status,
    isAuthenticated: status === "authenticated",
    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    register: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    logout: logoutMutation.mutateAsync,
    isLoggingOut: logoutMutation.isPending,
  };
}
