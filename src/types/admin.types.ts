import type { UserRole } from "@/types/auth.types";

export type { UserRole };

export interface AdminUser {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  organizationName: string | null;
  avatarUrl: string | null;
  phoneNumber: string | null;
  accountType: string | null;
  cooperativeId: string | null;
  phoneVerified: boolean;
  profileCompleted: boolean;
  isActive: boolean;
  createdAt: string;
}

export interface CreateAdminUserPayload {
  fullName: string;
  email: string;
  password: string;
  role: UserRole;
  organizationName?: string | null;
}

export interface UpdateAdminUserPayload {
  fullName?: string;
  organizationName?: string;
  role?: UserRole;
  isActive?: boolean;
  resetPassword?: string;
}

export const USER_ROLE_LABELS: Record<UserRole, string> = {
  ADMINISTRATOR: "Administrator",
  LOGISTICS_MANAGER: "Logistics Manager",
  FARMER_COOPERATIVE: "Farmer Cooperative",
  MARKET_ANALYST: "Market Analyst",
};

export const USER_ROLE_OPTIONS = Object.keys(USER_ROLE_LABELS) as UserRole[];