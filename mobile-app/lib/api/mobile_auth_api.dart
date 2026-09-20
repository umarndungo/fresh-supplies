import 'api_client.dart';
import '../models/auth_models.dart';

/// POST /mobile/auth/otp/request, /otp/verify, /refresh.
/// Login OTP is by email (see backend/docs — switched from phone number).
/// Every account is now provisioned top-down by an administrator or
/// cooperative admin (see backend/docs/multitenancy_design.md) — there is no
/// self-service signup, so otp/request 404s for an unprovisioned email
/// instead of creating one.
class MobileAuthApi {
  final _dio = ApiClient.instance.dio;

  /// Returns expires_in_seconds. Note: unlike most endpoints, this one is
  /// NOT wrapped in {"data": ...} — see otp_service.request_otp, which
  /// returns the raw dict directly.
  Future<int> requestOtp(String email) async {
    try {
      final res = await _dio.post('/mobile/auth/otp/request', data: {'email': email});
      return res.data['expires_in_seconds'] as int? ?? 300;
    } catch (e) {
      throw ApiClient.toApiException(e);
    }
  }

  Future<AuthTokens> verifyOtp(String email, String code) async {
    try {
      final res = await _dio.post('/mobile/auth/otp/verify', data: {'email': email, 'code': code});
      return AuthTokens.fromJson(res.data['data'] as Map<String, dynamic>);
    } catch (e) {
      throw ApiClient.toApiException(e);
    }
  }

  /// Shared with the web app (not under /mobile) — completes first login for
  /// a top-down provisioned account. Fails with a 409 if a password is
  /// already set; see backend/app/application/auth_service.py::set_password.
  Future<void> setPassword(String newPassword) async {
    try {
      await _dio.post('/auth/set-password', data: {'newPassword': newPassword});
    } catch (e) {
      throw ApiClient.toApiException(e);
    }
  }
}
