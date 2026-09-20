import 'api_client.dart';

/// POST /mobile/devices/register.
///
/// This only registers a token with the backend's DeviceTokenRepository —
/// there is no real push-sending integration (FCM/APNs) anywhere in this
/// project yet (flagged when Phase 2's driver-assignment notification was
/// skipped for the same reason). Until a real messaging plugin is wired up,
/// `token` here is a locally-generated placeholder, not a real push token —
/// this call exists so the registration endpoint is exercised, not to
/// claim push notifications work end to end.
class DeviceApi {
  final _dio = ApiClient.instance.dio;

  Future<void> registerDevice({required String token, required String platform}) async {
    try {
      await _dio.post('/mobile/devices/register', data: {'deviceToken': token, 'platform': platform});
    } catch (e) {
      throw ApiClient.toApiException(e);
    }
  }
}
