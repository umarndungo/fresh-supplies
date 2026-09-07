"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  mobileOtpRequestRequest,
  mobileOtpVerifyRequest,
  mobileAuthRefreshRequest,
  mobileCompleteProfileRequest,
  mobileShipmentsSyncRequest,
  mobileShipmentsPhotoUploadRequest,
  mobileShipmentsSyncStatusRequest,
  mobileShipmentsRecommendationRequest,
  mobileDriverManifestRequest,
  mobileDriverConfirmStopRequest,
  mobileDevicesRegisterRequest,
} from "@/lib/api/mobile.api";
import { ApiError } from "@/lib/api/api-error";

const MOBILE_QUERY_KEY = ["mobile"] as const;

export function useMobileOtpRequest(phone: string) {
  return useQuery({
    queryKey: [...MOBILE_QUERY_KEY, "otp-request", phone],
    queryFn: () => mobileOtpRequestRequest(phone),
    enabled: !!phone,
  });
}

export function useMobileOtpVerify(otp: string) {
  return useQuery({
    queryKey: [...MOBILE_QUERY_KEY, "otp-verify", otp],
    queryFn: () => mobileOtpVerifyRequest(otp),
    enabled: !!otp,
  });
}

export function useMobileAuthRefresh() {
  return useQuery({
    queryKey: [...MOBILE_QUERY_KEY, "auth-refresh"],
    queryFn: () => mobileAuthRefreshRequest(),
  });
}

export function useMobileCompleteProfile(payload: {
  fullName: string;
  accountType?: string;
  cooperative?: string;
}) {
  return useMutation({
    mutationFn: (data: {
      fullName: string;
      accountType?: string;
      cooperative?: string;
    }) => mobileCompleteProfileRequest(data),
    onSuccess: () => {
      toast.success("Profile completed.");
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to complete profile.");
    },
  });
}

export function useMobileShipmentsSync() {
  return useMutation({
    mutationFn: () => mobileShipmentsSyncRequest(),
    onSuccess: () => {
      toast.success("Shipments synced.");
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to sync shipments.");
    },
  });
}

export function useMobileShipmentsPhotoUpload() {
  return useMutation({
    mutationFn: (formData: FormData) => mobileShipmentsPhotoUploadRequest(formData),
    onSuccess: () => {
      toast.success("Photo uploaded.");
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to upload photo.");
    },
  });
}

export function useMobileShipmentsSyncStatus(clientIds: string[]) {
  return useMutation({
    mutationFn: (ids: string[]) => mobileShipmentsSyncStatusRequest(ids),
    onSuccess: () => {
      toast.success("Sync status checked.");
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to check sync status.");
    },
  });
}

export function useMobileShipmentsRecommendation(shipmentId: string) {
  return useQuery({
    queryKey: [...MOBILE_QUERY_KEY, "shipment-recommendation", shipmentId],
    queryFn: () => mobileShipmentsRecommendationRequest(shipmentId),
    enabled: !!shipmentId,
  });
}

export function useMobileDriverManifest() {
  return useQuery({
    queryKey: [...MOBILE_QUERY_KEY, "driver-manifest"],
    queryFn: () => mobileDriverManifestRequest(),
  });
}

export function useMobileDriverConfirmStop(stopId: string, location: { latitude: number; longitude: number }) {
  return useMutation({
    mutationFn: (vars: {
      stopId: string;
      latitude: number;
      longitude: number;
    }) => mobileDriverConfirmStopRequest(vars.stopId, { latitude:  vars.latitude, longitude: vars.longitude }),
    onSuccess: () => {
      toast.success("Stop confirmed.");
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to confirm stop.");
    },
  });
}

export function useMobileDevicesRegister(token: string) {
  return useMutation({
    mutationFn: (token: string) => mobileDevicesRegisterRequest(token),
    onSuccess: () => {
      toast.success("Device registered.");
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Unable to register device.");
    },
  });
}