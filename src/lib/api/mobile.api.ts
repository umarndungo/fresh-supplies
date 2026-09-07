import { apiClient } from "@/lib/api/client";
import { API_ENDPOINTS } from "@/lib/api/endpoints";
import type { ApiSuccessResponse } from "@/types/api.types";
import type { ApiError } from "@/lib/api/api-error";

export async function mobileOtpRequestRequest(phone: string): Promise<ApiSuccessResponse<unknown>> {
  const { data } = await apiClient.post<ApiSuccessResponse<unknown>>(API_ENDPOINTS.mobile.auth.otpRequest, { phone });
  return data;
}

export async function mobileOtpVerifyRequest(otp: string): Promise<ApiSuccessResponse<unknown>> {
  const { data } = await apiClient.post<ApiSuccessResponse<unknown>>(API_ENDPOINTS.mobile.auth.otpVerify, { otp });
  return data;
}

export async function mobileAuthRefreshRequest(): Promise<ApiSuccessResponse<unknown>> {
  const { data } = await apiClient.post<ApiSuccessResponse<unknown>>(API_ENDPOINTS.mobile.auth.refresh);
  return data;
}

export async function mobileCompleteProfileRequest(payload: {
  fullName: string;
  accountType?: string;
  cooperative?: string;
}): Promise<ApiSuccessResponse<unknown>> {
  const { data } = await apiClient.post<ApiSuccessResponse<unknown>>(
    API_ENDPOINTS.mobile.auth.completeProfile,
    payload
  );
  return data;
}

export async function mobileShipmentsSyncRequest(): Promise<ApiSuccessResponse<unknown>> {
  const { data } = await apiClient.post<ApiSuccessResponse<unknown>>(API_ENDPOINTS.mobile.shipments.sync);
  return data;
}

export async function mobileShipmentsPhotoUploadRequest(formData: FormData): Promise<ApiSuccessResponse<unknown>> {
  const { data } = await apiClient.post<ApiSuccessResponse<unknown>>(
    API_ENDPOINTS.mobile.shipments.photoUpload,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    }
  );
  return data;
}

export async function mobileShipmentsSyncStatusRequest(clientIds: string[]): Promise<ApiSuccessResponse<unknown>> {
  const { data } = await apiClient.post<ApiSuccessResponse<unknown>>(
    API_ENDPOINTS.mobile.shipments.syncStatus,
    { clientIds }
  );
  return data;
}

export async function mobileShipmentsRecommendationRequest(
  shipmentId: string
): Promise<ApiSuccessResponse<unknown>> {
  const { data } = await apiClient.get<ApiSuccessResponse<unknown>>(
    API_ENDPOINTS.mobile.shipments.recommendation.replace("{id}", shipmentId)
  );
  return data;
}

export async function mobileDriverManifestRequest(): Promise<ApiSuccessResponse<unknown>> {
  const { data } = await apiClient.get<ApiSuccessResponse<unknown>>(API_ENDPOINTS.mobile.driver.manifest);
  return data;
}

export async function mobileDriverConfirmStopRequest(
  stopId: string,
  location: { latitude: number; longitude: number }
): Promise<ApiSuccessResponse<unknown>> {
  const { data } = await apiClient.post<ApiSuccessResponse<unknown>>(
    API_ENDPOINTS.mobile.driver.confirmStop.replace("{id}", stopId),
    location
  );
  return data;
}

export async function mobileDevicesRegisterRequest(token: string): Promise<ApiSuccessResponse<unknown>> {
  const { data } = await apiClient.post<ApiSuccessResponse<unknown>>(
    API_ENDPOINTS.mobile.devices.register,
    { token }
  );
  return data;
}