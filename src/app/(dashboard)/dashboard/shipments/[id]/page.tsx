import { ShipmentDetailView } from "@/components/shipments/shipment-detail-view";

export default async function ShipmentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <ShipmentDetailView id={id} />;
}