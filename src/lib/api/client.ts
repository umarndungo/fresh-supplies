import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { env } from "@/lib/env";
import { API_ENDPOINTS } from "@/lib/api/endpoints";
import { ApiError } from "@/lib/api/api-error";

let accessToken: string | null = null;

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function clearAccessToken(): void {
  accessToken = null;
}

export const apiClient = axios.create({
  baseURL: env.NEXT_PUBLIC_API_URL,
  withCredentials: true,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});

type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean };

let isRefreshing = false;
let refreshQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null) {
  refreshQueue.forEach(({ resolve, reject }) => {
    if (error || !token) reject(error);
    else resolve(token);
  });
  refreshQueue = [];
}

function normalizeError(error: AxiosError): ApiError {
  const status = error.response?.status ?? 0;
  const payload = error.response?.data as
    | { message?: string; errors?: { field?: string; message: string }[] }
    | undefined;
  return new ApiError(
    payload?.message ?? error.message ?? "An unexpected error occurred.",
    status,
    payload?.errors
  );
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableConfig | undefined;

    const isRefreshCall = originalRequest?.url?.includes(API_ENDPOINTS.auth.refresh);

    if (!originalRequest || error.response?.status !== 401 || originalRequest._retry || isRefreshCall) {
      return Promise.reject(normalizeError(error));
    }

    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        refreshQueue.push({ resolve, reject });
      }).then((token) => {
        originalRequest.headers.set("Authorization", `Bearer ${token}`);
        return apiClient(originalRequest);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const { data } = await apiClient.post<{ accessToken: string }>(API_ENDPOINTS.auth.refresh);
      setAccessToken(data.accessToken);
      processQueue(null, data.accessToken);
      originalRequest.headers.set("Authorization", `Bearer ${data.accessToken}`);
      return apiClient(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      clearAccessToken();
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("freshroute:session-expired"));
      }
      return Promise.reject(normalizeError(error));
    } finally {
      isRefreshing = false;
    }
  }
);
