import 'api_client.dart';
import '../models/driver_models.dart';

/// GET /mobile/driver/manifest, POST /mobile/driver/stops/{id}/confirm.
class DriverApi {
  final _dio = ApiClient.instance.dio;

  Future<List<ManifestStop>> getManifest(DateTime date) async {
    try {
      final res = await _dio.get('/mobile/driver/manifest', queryParameters: {
        'date': date.toUtc().toIso8601String(),
      });
      final stops = res.data['stops'] as List;
      return stops.map((s) => ManifestStop.fromJson(s as Map<String, dynamic>)).toList();
    } catch (e) {
      throw ApiClient.toApiException(e);
    }
  }

  /// Idempotent server-side (backend/app/infrastructure/driver_repository.py
  /// confirm_stop: a second confirm on an already-IN_TRANSIT shipment
  /// returns "already_confirmed" rather than erroring) — matches Screen 9's
  /// disabled-after-first-tap UI, which is the client-side half of that.
  Future<String> confirmStop(String shipmentId, {required double lat, required double lon}) async {
    try {
      final res = await _dio.post('/mobile/driver/stops/$shipmentId/confirm', data: {
        'confirmedAt': DateTime.now().toUtc().toIso8601String(),
        'location': {'lat': lat, 'lon': lon},
      });
      return res.data['status'] as String;
    } catch (e) {
      throw ApiClient.toApiException(e);
    }
  }
}
