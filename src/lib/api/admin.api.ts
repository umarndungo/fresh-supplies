import { apiClient } from "@/lib/api/client";
import { API_ENDPOINTS } from "@/lib/api/endpoints";
import type { ApiSuccessResponse } from "@/types/api.types";
import type { AdminUser, CreateAdminUserPayload, UpdateAdminUserPayload } from "@/types/admin.types";
import type { CreateGrantPayload, Grant, Tenant, TenantUsage } from "@/types/tenant.types";

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

export async function listTenantsRequest(): Promise<Tenant[]> {
  const { data } = await apiClient.get<ApiSuccessResponse<Tenant[]>>(API_ENDPOINTS.admin.tenants.base);
  return data.data;
}

export async function createTenantRequest(payload: {
  name: string;
  adminEmail?: string;
  adminFullName?: string;
}): Promise<Tenant> {
  const { data } = await apiClient.post<ApiSuccessResponse<Tenant>>(API_ENDPOINTS.admin.tenants.base, payload);
  return data.data;
}

export async function updateTenantRequest(id: string, payload: { name: string }): Promise<Tenant> {
  const { data } = await apiClient.patch<ApiSuccessResponse<Tenant>>(API_ENDPOINTS.admin.tenants.byId(id), payload);
  return data.data;
}

export async function listTenantUsageRequest(): Promise<TenantUsage[]> {
  const { data } = await apiClient.get<ApiSuccessResponse<TenantUsage[]>>(API_ENDPOINTS.admin.tenants.usage);
  return data.data;
}

export async function getTenantUsageRequest(id: string): Promise<TenantUsage> {
  const { data } = await apiClient.get<ApiSuccessResponse<TenantUsage>>(API_ENDPOINTS.admin.tenants.usageById(id));
  return data.data;
}

export async function createGrantRequest(payload: CreateGrantPayload): Promise<Grant> {
  const { data } = await apiClient.post<ApiSuccessResponse<Grant>>(API_ENDPOINTS.admin.grants.base, payload);
  return data.data;
}

export async function listGrantsForTenantRequest(id: string): Promise<Grant[]> {
  const { data } = await apiClient.get<ApiSuccessResponse<Grant[]>>(API_ENDPOINTS.admin.tenants.grants(id));
  return data.data;
}

export async function revokeGrantRequest(id: string): Promise<void> {
  await apiClient.delete(API_ENDPOINTS.admin.grants.byId(id));
}

export async function listCooperativeMembersRequest(): Promise<AdminUser[]> {
  const { data } = await apiClient.get<ApiSuccessResponse<AdminUser[]>>(API_ENDPOINTS.cooperative.members.base);
  return data.data;
}

export async function createCooperativeMemberRequest(payload: {
  fullName: string;
  email: string;
  role: "FARMER_COOPERATIVE" | "DRIVER";
}): Promise<AdminUser> {
  const { data } = await apiClient.post<ApiSuccessResponse<AdminUser>>(
    API_ENDPOINTS.cooperative.members.base,
    payload
  );
  return data.data;
}