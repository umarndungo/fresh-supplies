/// Mirrors ShipmentSyncItem — one locally-captured shipment queued for sync.
/// client_id is generated once at capture time (Screen 4) and reused on
/// every retry, which is what makes /mobile/shipments/sync idempotent.
class QueuedCapture {
  final String clientId;
  final String crop;
  final double quantityKg;
  final DateTime capturedAt;
  final double lat;
  final double lon;
  final String? photoRef;
  final String? notes;
  final QueueStatus status;
  final String? error;
  final String? serverId;
  final String? riskTier;

  const QueuedCapture({
    required this.clientId,
    required this.crop,
    required this.quantityKg,
    required this.capturedAt,
    required this.lat,
    required this.lon,
    this.photoRef,
    this.notes,
    this.status = QueueStatus.pending,
    this.error,
    this.serverId,
    this.riskTier,
  });

  QueuedCapture copyWith({QueueStatus? status, String? error, String? serverId, String? riskTier}) => QueuedCapture(
        clientId: clientId,
        crop: crop,
        quantityKg: quantityKg,
        capturedAt: capturedAt,
        lat: lat,
        lon: lon,
        photoRef: photoRef,
        notes: notes,
        status: status ?? this.status,
        error: error,
        serverId: serverId ?? this.serverId,
        riskTier: riskTier ?? this.riskTier,
      );

  Map<String, dynamic> toSyncJson() => {
        'clientId': clientId,
        'crop': crop,
        'quantityKg': quantityKg,
        'capturedAt': capturedAt.toUtc().toIso8601String(),
        'location': {'lat': lat, 'lon': lon},
        if (photoRef != null) 'photoRef': photoRef,
        if (notes != null) 'notes': notes,
      };

  Map<String, dynamic> toStorageJson() => {
        ...toSyncJson(),
        'status': status.name,
        if (error != null) 'error': error,
        if (serverId != null) 'serverId': serverId,
        if (riskTier != null) 'riskTier': riskTier,
      };

  factory QueuedCapture.fromStorageJson(Map<String, dynamic> json) => QueuedCapture(
        clientId: json['clientId'] as String,
        crop: json['crop'] as String,
        quantityKg: (json['quantityKg'] as num).toDouble(),
        capturedAt: DateTime.parse(json['capturedAt'] as String),
        lat: (json['location']['lat'] as num).toDouble(),
        lon: (json['location']['lon'] as num).toDouble(),
        photoRef: json['photoRef'] as String?,
        notes: json['notes'] as String?,
        status: QueueStatus.values.byName(json['status'] as String? ?? 'pending'),
        error: json['error'] as String?,
        serverId: json['serverId'] as String?,
        riskTier: json['riskTier'] as String?,
      );
}

enum QueueStatus { pending, synced, failed }

/// One row of the sync response — mirrors ShipmentSyncResultItem.
class SyncResult {
  final String clientId;
  final String status; // "created" | "failed" (backend-defined)
  final String? serverId;
  final String? riskTier;
  final String? error;

  const SyncResult({required this.clientId, required this.status, this.serverId, this.riskTier, this.error});

  factory SyncResult.fromJson(Map<String, dynamic> json) => SyncResult(
        clientId: json['clientId'] as String,
        status: json['status'] as String,
        serverId: json['serverId'] as String?,
        riskTier: json['riskTier'] as String?,
        error: json['error'] as String?,
      );
}

/// Mirrors MobileRecommendationResponse.
class RecommendationResult {
  final String riskTier;
  final String riskLabel;
  final Map<String, dynamic>? recommendedMarket;
  final List<Map<String, dynamic>> alternateMarkets;

  const RecommendationResult({
    required this.riskTier,
    required this.riskLabel,
    required this.recommendedMarket,
    required this.alternateMarkets,
  });

  factory RecommendationResult.fromJson(Map<String, dynamic> json) => RecommendationResult(
        riskTier: json['riskTier'] as String,
        riskLabel: json['riskLabel'] as String,
        recommendedMarket: json['recommendedMarket'] as Map<String, dynamic>?,
        alternateMarkets: (json['alternateMarkets'] as List? ?? []).cast<Map<String, dynamic>>(),
      );
}
