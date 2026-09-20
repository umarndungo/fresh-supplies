import 'package:dio/dio.dart';

import 'app_config.dart';
import 'language_store.dart';
import 'token_store.dart';

class ApiException implements Exception {
  final int? statusCode;
  final String message;
  const ApiException(this.statusCode, this.message);

  @override
  String toString() => message;
}

/// Callback invoked when the session can no longer be refreshed (refresh
/// token expired/invalid) — the app should route back to /auth/phone. Set
/// once from main.dart; kept decoupled from the router so this file has no
/// UI dependency.
typedef OnSessionExpired = void Function();

/// Single shared Dio instance for every /mobile/* call:
/// - attaches the bearer token + Accept-Language to every request
/// - on a 401, attempts exactly one silent refresh (POST /mobile/auth/refresh)
///   and retries the original request; if that also fails, clears the
///   session and calls onSessionExpired.
class ApiClient {
  ApiClient._();
  static final ApiClient instance = ApiClient._();

  OnSessionExpired? onSessionExpired;

  late final Dio dio = Dio(BaseOptions(
    baseUrl: AppConfig.apiBaseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 15),
  ))
    ..interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await TokenStore.instance.accessToken;
        if (token != null) options.headers['Authorization'] = 'Bearer $token';
        options.headers['Accept-Language'] = LanguageStore.instance.current;
        handler.next(options);
      },
      onError: (error, handler) async {
        final isAuthRoute = error.requestOptions.path.contains('/mobile/auth/');
        if (error.response?.statusCode == 401 && !isAuthRoute) {
          final refreshed = await _tryRefresh();
          if (refreshed) {
            try {
              final clone = await dio.fetch(error.requestOptions);
              return handler.resolve(clone);
            } catch (_) {
              // fall through to session-expired handling below
            }
          }
          await TokenStore.instance.clear();
          onSessionExpired?.call();
        }
        handler.next(error);
      },
    ));

  bool _refreshing = false;

  Future<bool> _tryRefresh() async {
    if (_refreshing) return false; // avoid a refresh storm from parallel 401s
    _refreshing = true;
    try {
      final refreshToken = await TokenStore.instance.refreshToken;
      if (refreshToken == null) return false;
      final response = await dio.post('/mobile/auth/refresh', data: {'refreshToken': refreshToken});
      final data = response.data['data'];
      await TokenStore.instance.updateAccessToken(data['accessToken'] as String);
      return true;
    } catch (_) {
      return false;
    } finally {
      _refreshing = false;
    }
  }

  /// Normalizes Dio/backend errors into the app's error shape. The backend's
  /// AppError envelope is {"message": ..., "errors": [...], "statusCode": N}.
  static ApiException toApiException(Object error) {
    if (error is DioException) {
      final data = error.response?.data;
      final message = (data is Map && data['message'] is String) ? data['message'] as String : error.message ?? 'Something went wrong.';
      return ApiException(error.response?.statusCode, message);
    }
    return ApiException(null, error.toString());
  }
}
