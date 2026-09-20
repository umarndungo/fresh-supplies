/// Mirrors DriverManifestStop. Rendered exactly as returned — cooperative
/// pickups are already grouped server-side into one stop per collection
/// point (see backend/app/infrastructure/driver_repository.py), so this
/// model does not re-fragment or re-group anything client-side.
class ManifestStop {
  final String shipmentId;
  final String ownerType;
  final String? cooperativeName;
  final String crop;
  final double quantityKg;
  final double lat;
  final double lon;
  final String pickupLabel;
  final String destinationMarket;
  final String riskTier;
  final int sequence;

  const ManifestStop({
    required this.shipmentId,
    required this.ownerType,
    required this.cooperativeName,
    required this.crop,
    required this.quantityKg,
    required this.lat,
    required this.lon,
    required this.pickupLabel,
    required this.destinationMarket,
    required this.riskTier,
    required this.sequence,
  });

  factory ManifestStop.fromJson(Map<String, dynamic> json) {
    final pickup = json['pickupLocation'] as Map<String, dynamic>? ?? const {};
    return ManifestStop(
      shipmentId: json['shipmentId'] as String,
      ownerType: json['ownerType'] as String,
      cooperativeName: json['cooperativeName'] as String?,
      crop: json['crop'] as String,
      quantityKg: (json['quantityKg'] as num).toDouble(),
      lat: (pickup['lat'] as num?)?.toDouble() ?? 0.0,
      lon: (pickup['lon'] as num?)?.toDouble() ?? 0.0,
      pickupLabel: pickup['label'] as String? ?? '',
      destinationMarket: json['destinationMarket'] as String,
      riskTier: json['riskTier'] as String,
      sequence: json['sequence'] as int,
    );
  }
}
