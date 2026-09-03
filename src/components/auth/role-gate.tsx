"use client";

import type { ReactNode } from "react";
import { useAuthContext } from "@/context/auth-context";
import type { UserRole } from "@/types/auth.types";

interface RoleGateProps {
  allowed: UserRole[];
  children: ReactNode;
  fallback?: ReactNode;
}

export function RoleGate({ allowed, children, fallback = null }: RoleGateProps) {
  const { user } = useAuthContext();
  if (!user || !allowed.includes(user.role)) return <>{fallback}</>;
  return <>{children}</>;
}
