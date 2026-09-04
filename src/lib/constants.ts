import type { UserRole } from "@/types/auth.types";

export const APP_NAME = "Fresh Supplies";

/** Non-sensitive flag cookie read by middleware.ts to gate routes at the edge. */
export const SESSION_FLAG_COOKIE = "frs_session";

export const ROUTES = {
  home: "/",
  login: "/login",
  register: "/register",
  dashboard: "/dashboard",
} as const;

export const ROLE_LABELS: Record<UserRole, string> = {
  ADMINISTRATOR: "Administrator",
  LOGISTICS_MANAGER: "Logistics Manager",
  FARMER_COOPERATIVE: "Farmer Cooperative",
  MARKET_ANALYST: "Market Analyst",
};

export const ROLE_OPTIONS: { value: UserRole; label: string }[] = (
  Object.entries(ROLE_LABELS) as [UserRole, string][]
).map(([value, label]) => ({ value, label }));
