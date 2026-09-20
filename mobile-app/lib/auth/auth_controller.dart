import 'package:flutter/foundation.dart';

import '../api/token_store.dart';
import '../models/auth_models.dart';

enum AuthStatus { unknown, loggedOut, needsProfile, loggedIn }

/// Single source of truth for session state, read by the router's redirect
/// logic (see router.dart) so every screen doesn't re-implement its own
/// "am I logged in" check.
class AuthController extends ChangeNotifier {
  AuthController._();
  static final AuthController instance = AuthController._();

  AuthStatus status = AuthStatus.unknown;
  String? role;

  Future<void> bootstrap() async {
    try {
      final loggedIn = await TokenStore.instance.isLoggedIn;
      if (!loggedIn) {
        status = AuthStatus.loggedOut;
      } else {
        final profileDone = await TokenStore.instance.profileCompleted;
        role = await TokenStore.instance.role;
        status = profileDone ? AuthStatus.loggedIn : AuthStatus.needsProfile;
      }
    } catch (_) {
      // Secure storage unavailable (e.g. a platform/browser without
      // Keychain/Keystore support configured) — fail safe to logged-out
      // rather than leaving the app stuck with status == unknown forever,
      // which would show a permanently blank screen (no route ever matches).
      status = AuthStatus.loggedOut;
    }
    notifyListeners();
  }

  Future<void> onOtpVerified(AuthTokens tokens) async {
    await TokenStore.instance.saveSession(
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
      userId: tokens.user.id,
      profileCompleted: tokens.user.profileCompleted,
      role: tokens.user.role,
    );
    role = tokens.user.role;
    status = tokens.user.profileCompleted ? AuthStatus.loggedIn : AuthStatus.needsProfile;
    notifyListeners();
  }

  Future<void> onProfileCompleted() async {
    await TokenStore.instance.setProfileCompleted(true);
    status = AuthStatus.loggedIn;
    notifyListeners();
  }

  Future<void> logout() async {
    await TokenStore.instance.clear();
    status = AuthStatus.loggedOut;
    role = null;
    notifyListeners();
  }
}
