export type ShipmentStatus = "SCHEDULED" | "IN_TRANSIT" | "DELIVERED" | "CANCELLED";

export type RiskTier = "Fresh" | "At-Risk" | "Critical";

export interface Shipment {
  id: string;
  origin: string;
  destination: string;
  produceType: string;
  status: ShipmentStatus;
  scheduledDate: string;
  deliveryDate: string | null;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  // ML prediction fields (populated on demand)
  latitude?: number;
  longitude?: number;
  temperatureC?: number;
  transitDurationHr?: number;
  pressurePsi?: number;
  baselineLossPct?: number;
  quantityKg?: number;
  spoilageProbability?: number;
  riskTier?: RiskTier;
  spoilPrediction?: boolean;
}

export interface CreateShipmentPayload {
  origin: string;
  destination: string;
  produceType: string;
  scheduledDate: string;
  // ML prediction fields
  latitude?: number;
  longitude?: number;
  temperatureC?: number;
  transitDurationHr?: number;
  pressurePsi?: number;
  baselineLossPct?: number;
  quantityKg?: number;
}

export interface UpdateShipmentPayload {
  status?: ShipmentStatus;
  deliveryDate?: string | null;
}
