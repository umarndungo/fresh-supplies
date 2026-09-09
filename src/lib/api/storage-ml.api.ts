import { apiClient } from "@/lib/api/client";
import { API_ENDPOINTS } from "@/lib/api/endpoints";
import type { Produce } from "@/types/produce.types";

export interface StorageSpoilageResult {
  storage_age_hours: number;
  storage_spoilage_probability: number;
  storage_risk_tier: string;
  storage_spoil_prediction: boolean;
  estimated_shelf_life_days: number;
}

export async function predictStorageSpoilageRequest(produce: Produce): Promise<StorageSpoilageResult> {
  const { data } = await apiClient.post<StorageSpoilageResult>(API_ENDPOINTS.ml.predictStorageSpoilage, {
    crop_type: produce.name,
    harvest_date: produce.harvestDate,
    storage_temperature_c: produce.storageTemperatureC ?? 25,
    storage_pressure_psi: produce.storagePressurePsi ?? 30,
    quality_grade: produce.qualityGrade,
    quantity_kg: produce.quantityKg,
  });
  return data;
}