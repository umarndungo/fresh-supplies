import { apiClient } from "@/lib/api/client";
import { API_ENDPOINTS } from "@/lib/api/endpoints";
import type { ApiSuccessResponse } from "@/types/api.types";
import type { AdminUser, CreateAdminUserPayload, UpdateAdminUserPayload } from "@/types/admin.types";

export async function listAdminUsersRequest(): Promise<AdminUser[]> {
  const { data } = await apiClient.get<ApiSuccessResponse<AdminUser[]>>(API_ENDPOINTS.admin.users.base);
  return data.data;
}

export async function createAdminUserRequest(payload: CreateAdminUserPayload): Promise<AdminUser> {
  const { data } = await apiClient.post<ApiSuccessResponse<AdminUser>>(API_ENDPOINTS.admin.users.base, payload);
  return data.data;
}

export async function updateAdminUserRequest(id: string, payload: UpdateAdminUserPayload): Promise<AdminUser> {
  const { data } = await apiClient.patch<ApiSuccessResponse<AdminUser>>(API_ENDPOINTS.admin.users.byId(id), payload);
  return data.data;
}

export async function deleteAdminUserRequest(id: string): Promise<void> {
  await apiClient.delete(API_ENDPOINTS.admin.users.byId(id));
}