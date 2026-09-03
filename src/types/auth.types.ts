export type UserRole =
  | "ADMINISTRATOR"
  | "LOGISTICS_MANAGER"
  | "FARMER_COOPERATIVE"
  | "MARKET_ANALYST";

export interface AuthUser {
  id: string;
  email: string;
  fullName: string;
  role: UserRole;
  organizationName: string | null;
  avatarUrl: string | null;
  createdAt: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterPayload {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
  role: UserRole;
  organizationName?: string;
}

export interface AuthTokensResponse {
  accessToken: string;
  expiresIn: number;
  user: AuthUser;
}
