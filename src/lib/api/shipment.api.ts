import { apiClient } from "@/lib/api/client";
import { API_ENDPOINTS } from "@/lib/api/endpoints";
import type { ApiSuccessResponse } from "@/types/api.types";
import type { CreateShipmentPayload, Shipment, UpdateShipmentPayload } from "@/types/shipment.types";

export async function listShipmentsRequest(): Promise<Shipment[]> {
  const { data } = await apiClient.get<ApiSuccessResponse<Shipment[]>>(API_ENDPOINTS.shipments.base);
  return data.data;
}

export async function createShipmentRequest(payload: CreateShipmentPayload): Promise<Shipment> {
  const { data } = await apiClient.post<ApiSuccessResponse<Shipment>>(API_ENDPOINTS.shipments.base, payload);
  return data.data;
}

export async function updateShipmentRequest(id: string, payload: UpdateShipmentPayload): Promise<Shipment> {
  const { data } = await apiClient.patch<ApiSuccessResponse<Shipment>>(API_ENDPOINTS.shipments.byId(id), payload);
  return data.data;
}

export async function deleteShipmentRequest(id: string): Promise<void> {
  await apiClient.delete(API_ENDPOINTS.shipments.byId(id));
}
