export type CommodityClass = "PERISHABLE" | "STAPLE";
export type ProduceStatus = "AVAILABLE" | "RESERVED" | "SOLD" | "SPOILED";

export interface Produce {
  id: string;
  name: string;
  variety: string;
  quantityKg: number;
  unitPrice: number;
  qualityGrade: string;
  harvestDate: string;
  storageLocation: string;
  commodityClass: CommodityClass;
  cooperativeId: string;
  status: ProduceStatus;
  storageTemperatureC?: number;
  storagePressurePsi?: number;
  storageSpoilageProbability?: number;
  storageRiskTier?: string;
  storageSpoilPrediction?: boolean;
  estimatedShelfLifeDays?: number;
  createdAt: string;
  updatedAt: string;
}

export interface CreateProducePayload {
  name: string;
  variety: string;
  quantityKg: number;
  unitPrice: number;
  qualityGrade: string;
  harvestDate: string;
  storageLocation: string;
  commodityClass: CommodityClass;
  storageTemperatureC?: number;
  storagePressurePsi?: number;
}

export interface UpdateProducePayload {
  name?: string;
  variety?: string;
  quantityKg?: number;
  unitPrice?: number;
  qualityGrade?: string;
  harvestDate?: string;
  storageLocation?: string;
  commodityClass?: CommodityClass;
  status?: ProduceStatus;
  storageTemperatureC?: number;
  storagePressurePsi?: number;
  storageSpoilageProbability?: number;
  storageRiskTier?: string;
  storageSpoilPrediction?: boolean;
  estimatedShelfLifeDays?: number;
}