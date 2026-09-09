import { apiClient } from "@/lib/api/client";
import { API_ENDPOINTS } from "@/lib/api/endpoints";
import type { LocationSearchResult } from "@/types/location.types";

export async function searchLocationsRequest(query: string): Promise<LocationSearchResult[]> {
  const { data } = await apiClient.get<LocationSearchResult[]>(API_ENDPOINTS.locations.search, {
    params: { query },
  });
  return data;
}