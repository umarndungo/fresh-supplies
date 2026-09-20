import 'package:latlong2/latlong.dart';

import '../widgets/risk_tier_badge.dart';

/// Fixed crop list — mirrors the 9 crops the backend's post_harvest_data_engine
/// prices and predicts for (PROJECT_DOCUMENTATION.md §6.2). Phase 5 should
/// fetch this from an endpoint instead of hardcoding it a second time; kept
/// here only because Phase 4 has no API calls yet.
const List<String> kCropList = [
  'Tomatoes',
  'Bananas',
  'Mangoes',
  'Kale (Sukumawiki)',
  'Avocados',
  'Beans',
  'Onions',
  'Maize',
  'Potatoes',
];

class MockShipment {
  final String id;
  final String crop;
  final double quantityKg;
  final RiskTier riskTier;
  final String actionSentence;
  final MockMarketOption recommended;
  final List<MockMarketOption> alternates;

  const MockShipment({
    required this.id,
    required this.crop,
    required this.quantityKg,
    required this.riskTier,
    required this.actionSentence,
    required this.recommended,
    this.alternates = const [],
  });
}

class MockMarketOption {
  final String name;
  final double distanceKm;
  final double pricePerKg;
  final double estimatedRevenue;

  const MockMarketOption({
    required this.name,
    required this.distanceKm,
    required this.pricePerKg,
    required this.estimatedRevenue,
  });
}

/// Mock shipments for the signed-in farmer — Screen 0's list and Screen 6's
/// detail both read from this.
final List<MockShipment> kMockShipments = [
  MockShipment(
    id: 's1',
    crop: 'Tomatoes',
    quantityKg: 340,
    riskTier: RiskTier.critical,
    actionSentence: 'Sell within 6 hours — divert to Nakuru Wakulima now.',
    recommended: const MockMarketOption(
      name: 'Nakuru Wakulima Market',
      distanceKm: 42.0,
      pricePerKg: 78.0,
      estimatedRevenue: 21420.0,
    ),
    alternates: const [
      MockMarketOption(name: 'Naivasha Market', distanceKm: 58.0, pricePerKg: 74.0, estimatedRevenue: 19040.0),
      MockMarketOption(name: 'Nairobi Gikomba Market', distanceKm: 96.0, pricePerKg: 90.0, estimatedRevenue: 20400.0),
    ],
  ),
  MockShipment(
    id: 's2',
    crop: 'Avocados',
    quantityKg: 180,
    riskTier: RiskTier.atRisk,
    actionSentence: 'Sell within 24 hours to avoid quality loss.',
    recommended: const MockMarketOption(
      name: 'Thika Wholesale Market',
      distanceKm: 21.0,
      pricePerKg: 112.0,
      estimatedRevenue: 19152.0,
    ),
  ),
  MockShipment(
    id: 's3',
    crop: 'Maize',
    quantityKg: 600,
    riskTier: RiskTier.fresh,
    actionSentence: 'On track — no action needed today.',
    recommended: const MockMarketOption(
      name: 'Eldoret Central Market',
      distanceKm: 15.0,
      pricePerKg: 44.0,
      estimatedRevenue: 25872.0,
    ),
  ),
];

enum SyncQueueStatus { pending, synced, failed }

class MockQueueItem {
  final String id;
  final String crop;
  final double quantityKg;
  final SyncQueueStatus status;

  const MockQueueItem({required this.id, required this.crop, required this.quantityKg, required this.status});
}

final List<MockQueueItem> kMockQueue = [
  MockQueueItem(id: 'q1', crop: 'Tomatoes', quantityKg: 340, status: SyncQueueStatus.synced),
  MockQueueItem(id: 'q2', crop: 'Kale (Sukumawiki)', quantityKg: 90, status: SyncQueueStatus.pending),
  MockQueueItem(id: 'q3', crop: 'Bananas', quantityKg: 210, status: SyncQueueStatus.failed),
];

enum NotificationType { riskChange, manifestChange }

class MockNotification {
  final String id;
  final NotificationType type;
  final String title;
  final DateTime timestamp;
  final String? relatedShipmentId;

  const MockNotification({
    required this.id,
    required this.type,
    required this.title,
    required this.timestamp,
    this.relatedShipmentId,
  });
}

final List<MockNotification> kMockNotifications = [
  MockNotification(
    id: 'n1',
    type: NotificationType.riskChange,
    title: 'Tomatoes shipment moved to Critical',
    timestamp: DateTime.now().subtract(const Duration(minutes: 18)),
    relatedShipmentId: 's1',
  ),
  MockNotification(
    id: 'n2',
    type: NotificationType.manifestChange,
    title: 'New stop added to today\'s manifest',
    timestamp: DateTime.now().subtract(const Duration(hours: 2)),
  ),
];

class MockStop {
  final String id;
  final int sequence;
  final String collectionPointName;
  final String address;
  final String crop;
  final double quantityKg;
  final RiskTier riskTier;
  final LatLng point;
  final bool confirmed;

  const MockStop({
    required this.id,
    required this.sequence,
    required this.collectionPointName,
    required this.address,
    required this.crop,
    required this.quantityKg,
    required this.riskTier,
    required this.point,
    this.confirmed = false,
  });
}

final List<MockStop> kMockStops = [
  MockStop(
    id: 'st1',
    sequence: 1,
    collectionPointName: 'Kiambu Farmers Cooperative',
    address: 'Kiambu Rd, near Town Hall',
    crop: 'Tomatoes',
    quantityKg: 340,
    riskTier: RiskTier.critical,
    point: const LatLng(-1.1714, 36.8356),
  ),
  MockStop(
    id: 'st2',
    sequence: 2,
    collectionPointName: 'Thika Growers Union',
    address: 'Garissa Rd, Thika',
    crop: 'Avocados',
    quantityKg: 180,
    riskTier: RiskTier.atRisk,
    point: const LatLng(-1.0333, 37.0693),
  ),
  MockStop(
    id: 'st3',
    sequence: 3,
    collectionPointName: 'Ruiru Smallholders Group',
    address: 'Eastern Bypass, Ruiru',
    crop: 'Maize',
    quantityKg: 600,
    riskTier: RiskTier.fresh,
    point: const LatLng(-1.1499, 36.9622),
  ),
];
