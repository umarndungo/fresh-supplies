import 'package:dio/dio.dart';

import 'api_client.dart';
import '../models/shipment_models.dart';

/// POST /mobile/shipments/sync, /photo-upload; GET /sync-status,
/// /{id}/recommendation.
class ShipmentApi {
  final _dio = ApiClient.instance.dio;

  /// Idempotent on client_id — safe to call again with the same queued
  /// items after a partial failure (backend/docs mobile API contract).
  Future<List<SyncResult>> sync(List<QueuedCapture> items) async {
    try {
      final res = await _dio.post('/mobile/shipments/sync', data: {
        'shipments': items.map((i) => i.toSyncJson()).toList(),
      });
      final results = res.data['data']['results'] as List;
      return results.map((r) => SyncResult.fromJson(r as Map<String, dynamic>)).toList();
    } catch (e) {
      throw ApiClient.toApiException(e);
    }
  }

  Future<String> uploadPhoto({required String clientId, required String filePath}) async {
    try {
      final form = FormData.fromMap({
        'client_id': clientId,
        'file': await MultipartFile.fromFile(filePath),
      });
      final res = await _dio.post('/mobile/shipments/photo-upload', data: form);
      return res.data['photoRef'] as String;
    } catch (e) {
      throw ApiClient.toApiException(e);
    }
  }

  Future<RecommendationResult> getRecommendation({
    required String shipmentId,
    required String crop,
    required double quantityKg,
    required double lat,
    required double lon,
  }) async {
    try {
      final res = await _dio.get('/mobile/shipments/$shipmentId/recommendation', queryParameters: {
        'crop': crop,
        'quantityKg': quantityKg,
        'lat': lat,
        'lon': lon,
      });
      return RecommendationResult.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw ApiClient.toApiException(e);
    }
  }
}
