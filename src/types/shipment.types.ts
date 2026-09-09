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
  // Origin location (source)
  originLatitude?: number;
  originLongitude?: number;
  // Destination location (market)
  destinationLatitude?: number;
  destinationLongitude?: number;
  // ML prediction fields (populated on demand)
  temperatureC?: number;
  transitDurationHr?: number;
  pressurePsi?: number;
  baselineLossPct?: number;
  quantityKg?: number;
  spoilageProbability?: number;
  riskTier?: RiskTier;
  spoilPrediction?: boolean;
  marketRecommendations?: import("@/types/ml.types").MarketRecommendationOut[];
}

export interface CreateShipmentPayload {
  origin: string;
  destination: string;
  produceType: string;
  scheduledDate: string;
  // Origin location (source) - for ML predictions
  originLatitude?: number;
  originLongitude?: number;
  // Destination location (market) coordinates - auto-filled from market selection
  destinationLatitude?: number;
  destinationLongitude?: number;
  // ML prediction fields
  temperatureC?: number;
  transitDurationHr?: number;
  pressurePsi?: number;
  baselineLossPct?: number;
  quantityKg?: number;
}

export interface UpdateShipmentPayload {
  status?: ShipmentStatus;
  deliveryDate?: string | null;
  spoilageProbability?: number;
  riskTier?: RiskTier;
  spoilPrediction?: boolean;
  marketRecommendations?: import("@/types/ml.types").MarketRecommendationOut[];
}
