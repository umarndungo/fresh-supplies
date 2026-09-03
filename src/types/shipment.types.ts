export type ShipmentStatus = "SCHEDULED" | "IN_TRANSIT" | "DELIVERED" | "CANCELLED";

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
}

export interface CreateShipmentPayload {
  origin: string;
  destination: string;
  produceType: string;
  scheduledDate: string;
}

export interface UpdateShipmentPayload {
  status?: ShipmentStatus;
  deliveryDate?: string | null;
}
