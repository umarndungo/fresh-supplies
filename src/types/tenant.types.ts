export interface Tenant {
  id: string;
  name: string;
  createdBy: string;
  createdAt: string;
}

export interface TenantUsage {
  cooperativeId: string;
  memberCount: number;
  shipmentCount: number;
  produceItemCount: number;
  totalQuantityKg: number;
}

export interface Grant {
  id: string;
  userId: string;
  cooperativeId: string;
  grantedBy: string;
  createdAt: string;
}

export interface CreateGrantPayload {
  userId: string;
  cooperativeId: string;
}