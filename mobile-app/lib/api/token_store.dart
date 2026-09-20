import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Persists the mobile session's access/refresh tokens. Backed by
/// flutter_secure_storage (Keychain/Keystore) rather than shared_preferences
/// — these are bearer credentials, not app preferences.
class TokenStore {
  TokenStore._();
  static final TokenStore instance = TokenStore._();

  final _storage = const FlutterSecureStorage();

  static const _kAccess = 'access_token';
  static const _kRefresh = 'refresh_token';
  static const _kUserId = 'user_id';
  static const _kProfileCompleted = 'profile_completed';
  static const _kRole = 'role';

  Future<void> saveSession({
    required String accessToken,
    required String refreshToken,
    required String userId,
    required bool profileCompleted,
    required String role,
  }) async {
    await Future.wait([
      _storage.write(key: _kAccess, value: accessToken),
      _storage.write(key: _kRefresh, value: refreshToken),
      _storage.write(key: _kUserId, value: userId),
      _storage.write(key: _kProfileCompleted, value: profileCompleted.toString()),
      _storage.write(key: _kRole, value: role),
    ]);
  }

  Future<void> updateAccessToken(String accessToken) => _storage.write(key: _kAccess, value: accessToken);

  Future<String?> get accessToken => _storage.read(key: _kAccess);
  Future<String?> get refreshToken => _storage.read(key: _kRefresh);
  Future<String?> get userId => _storage.read(key: _kUserId);
  Future<String?> get role => _storage.read(key: _kRole);

  Future<bool> get profileCompleted async => (await _storage.read(key: _kProfileCompleted)) == 'true';

  Future<void> setProfileCompleted(bool value) => _storage.write(key: _kProfileCompleted, value: value.toString());

  Future<bool> get isLoggedIn async => (await accessToken) != null;

  Future<void> clear() async {
    await _storage.deleteAll();
  }
}
