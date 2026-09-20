import 'api_client.dart';
import '../models/location_models.dart';

/// GET /locations/search — the same Nominatim-backed geocoding endpoint the
/// web app's LocationPicker uses (src/components/map/location-picker.tsx),
/// scoped to Kenya. Not under /mobile — it's shared, generic-auth infra.
class LocationApi {
  final _dio = ApiClient.instance.dio;

  Future<List<LocationSearchResult>> search(String query) async {
    try {
      final res = await _dio.get('/locations/search', queryParameters: {'query': query});
      return (res.data as List)
          .map((e) => LocationSearchResult.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw ApiClient.toApiException(e);
    }
  }
}
