import { apiClient } from "@/lib/api/client";
import { API_ENDPOINTS } from "@/lib/api/endpoints";
import type { AuthTokensResponse, AuthUser, LoginCredentials } from "@/types/auth.types";
import type { ApiSuccessResponse } from "@/types/api.types";

export async function loginRequest(credentials: LoginCredentials): Promise<AuthTokensResponse> {
  const { data } = await apiClient.post<ApiSuccessResponse<AuthTokensResponse>>(
    API_ENDPOINTS.auth.login,
    credentials
  );
  return data.data;
}

export async function requestLoginOtpRequest(email: string): Promise<void> {
  await apiClient.post(API_ENDPOINTS.auth.otpRequest, { email });
}

export async function verifyLoginOtpRequest(email: string, code: string): Promise<AuthTokensResponse> {
  const { data } = await apiClient.post<ApiSuccessResponse<AuthTokensResponse>>(API_ENDPOINTS.auth.otpVerify, {
    email,
    code,
  });
  return data.data;
}

export async function setPasswordRequest(newPassword: string): Promise<AuthUser> {
  const { data } = await apiClient.post<ApiSuccessResponse<AuthUser>>(API_ENDPOINTS.auth.setPassword, {
    newPassword,
  });
  return data.data;
}

export async function fetchCurrentUserRequest(): Promise<AuthUser> {
  const { data } = await apiClient.get<ApiSuccessResponse<AuthUser>>(API_ENDPOINTS.auth.me);
  return data.data;
}

export async function logoutRequest(): Promise<void> {
  await apiClient.post(API_ENDPOINTS.auth.logout);
}
