/// Mirrors backend/app/application/location_schemas.py::LocationSearchResult.
/// Unlike most endpoints, /locations/search returns a raw list with
/// snake_case keys (no {"data": ...} envelope, no camelCase) — see
/// backend/app/api/routes/locations.py.
class LocationSearchResult {
  final String displayName;
  final double latitude;
  final double longitude;
  final String? type;
  final String? county;

  const LocationSearchResult({
    required this.displayName,
    required this.latitude,
    required this.longitude,
    this.type,
    this.county,
  });

  factory LocationSearchResult.fromJson(Map<String, dynamic> json) => LocationSearchResult(
        displayName: json['display_name'] as String,
        latitude: (json['latitude'] as num).toDouble(),
        longitude: (json['longitude'] as num).toDouble(),
        type: json['type'] as String?,
        county: json['county'] as String?,
      );
}
