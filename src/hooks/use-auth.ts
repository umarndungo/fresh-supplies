"use client";

import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuthContext } from "@/context/auth-context";
import { ApiError } from "@/lib/api/api-error";
import { ROUTES } from "@/lib/constants";
import type { LoginCredentials } from "@/types/auth.types";

export function useAuth() {
  const { user, status, login, requestLoginOtp, verifyLoginOtp, setPassword, logout } = useAuthContext();
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

  const requestOtpMutation = useMutation({
    mutationFn: (email: string) => requestLoginOtp(email),
    onSuccess: () => {
      toast.success("Code sent — check your email.");
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to send a sign-in code.");
    },
  });

  const verifyOtpMutation = useMutation({
    mutationFn: ({ email, code }: { email: string; code: string }) => verifyLoginOtp(email, code),
    onSuccess: (authUser) => {
      if (!authUser.profileCompleted) {
        router.push(ROUTES.setPassword);
        return;
      }
      toast.success(`Welcome back, ${authUser.fullName.split(" ")[0]}.`);
      router.push(ROUTES.dashboard);
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "That code didn't work. Please try again.");
    },
  });

  const setPasswordMutation = useMutation({
    mutationFn: (newPassword: string) => setPassword(newPassword),
    onSuccess: () => {
      toast.success("Password set. You're all set.");
      router.push(ROUTES.dashboard);
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to set your password.");
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
    requestOtp: requestOtpMutation.mutateAsync,
    isRequestingOtp: requestOtpMutation.isPending,
    verifyOtp: verifyOtpMutation.mutateAsync,
    isVerifyingOtp: verifyOtpMutation.isPending,
    setPassword: setPasswordMutation.mutateAsync,
    isSettingPassword: setPasswordMutation.isPending,
    logout: logoutMutation.mutateAsync,
    isLoggingOut: logoutMutation.isPending,
  };
}
