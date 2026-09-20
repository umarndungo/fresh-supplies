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
