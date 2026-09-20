export type UserRole =
  | "ADMINISTRATOR"
  | "LOGISTICS_MANAGER"
  | "FARMER_COOPERATIVE"
  | "MARKET_ANALYST"
  | "DRIVER";

export interface AuthUser {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  organizationName: string | null;
  avatarUrl: string | null;
  cooperativeId: string | null;
  cooperativeRole: "MEMBER" | "ADMIN" | null;
  profileCompleted: boolean;
  createdAt: string;
  /** Only present for LOGISTICS_MANAGER/MARKET_ANALYST — whether they have
   * at least one cooperative access grant. Distinguishes "no access
   * granted yet" from "granted, but that cooperative has no data yet",
   * which otherwise look identical as an empty shipments/produce list. */
  hasCooperativeAccess?: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthTokensResponse {
  accessToken: string;
  expiresIn: number;
  user: AuthUser;
}
