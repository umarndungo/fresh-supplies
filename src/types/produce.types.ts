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
}