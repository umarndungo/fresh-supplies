import { apiClient } from "@/lib/api/client";
import { API_ENDPOINTS } from "@/lib/api/endpoints";
import type { ApiSuccessResponse } from "@/types/api.types";
import type { CreateProducePayload, Produce, UpdateProducePayload } from "@/types/produce.types";

export async function listProduceRequest(): Promise<Produce[]> {
  const { data } = await apiClient.get<ApiSuccessResponse<Produce[]>>(API_ENDPOINTS.produce.base);
  return data.data;
}

export async function getProduceRequest(id: string): Promise<Produce> {
  const { data } = await apiClient.get<ApiSuccessResponse<Produce>>(API_ENDPOINTS.produce.byId(id));
  return data.data;
}

export async function createProduceRequest(payload: CreateProducePayload): Promise<Produce> {
  const { data } = await apiClient.post<ApiSuccessResponse<Produce>>(API_ENDPOINTS.produce.base, payload);
  return data.data;
}

export async function updateProduceRequest(id: string, payload: UpdateProducePayload): Promise<Produce> {
  const { data } = await apiClient.patch<ApiSuccessResponse<Produce>>(API_ENDPOINTS.produce.byId(id), payload);
  return data.data;
}

export async function deleteProduceRequest(id: string): Promise<void> {
  await apiClient.delete(API_ENDPOINTS.produce.byId(id));
}