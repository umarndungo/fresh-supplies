import 'package:go_router/go_router.dart';

import 'auth/auth_controller.dart';
import 'models/driver_models.dart';
import 'screens/auth/otp_verify_screen.dart';
import 'screens/auth/phone_entry_screen.dart';
import 'screens/capture/shipment_capture_screen.dart';
import 'screens/driver/driver_manifest_screen.dart';
import 'screens/driver/stop_detail_screen.dart';
import 'screens/home/farmer_home_screen.dart';
import 'screens/notifications/notifications_screen.dart';
import 'screens/auth/set_password_screen.dart';
import 'screens/recommendation/recommendation_screen.dart';
import 'screens/settings/settings_screen.dart';
import 'screens/sync/sync_status_screen.dart';

// Route path kept as /auth/email (renamed from /auth/phone when login OTP
// switched from phone/SMS to email — see PhoneEntryScreen's doc comment).
const _authRoutes = {'/auth/email', '/auth/verify'};
const _setPasswordRoute = '/auth/set-password';

/// Route table matching the build spec's screen list, now guarded by real
/// session state (Phase 5) instead of being freely reachable (Phase 4).
final appRouter = GoRouter(
  initialLocation: '/auth/email',
  refreshListenable: AuthController.instance,
  redirect: (context, state) {
    final status = AuthController.instance.status;
    final path = state.matchedLocation;

    if (status == AuthStatus.unknown) return null; // still bootstrapping

    if (status == AuthStatus.loggedOut) {
      return _authRoutes.contains(path) ? null : '/auth/email';
    }
    if (status == AuthStatus.needsProfile) {
      return path == _setPasswordRoute ? null : _setPasswordRoute;
    }
    // loggedIn: keep out of the auth/onboarding screens.
    if (_authRoutes.contains(path) || path == _setPasswordRoute) return '/home';
    return null;
  },
  routes: [
    GoRoute(path: '/auth/email', builder: (context, state) => const PhoneEntryScreen()),
    GoRoute(
      path: '/auth/verify',
      builder: (context, state) => OtpVerifyScreen(email: state.extra as String? ?? ''),
    ),
    GoRoute(path: '/auth/set-password', builder: (context, state) => const SetPasswordScreen()),
    GoRoute(path: '/home', builder: (context, state) => const FarmerHomeScreen()),
    GoRoute(path: '/capture/new', builder: (context, state) => const ShipmentCaptureScreen()),
    GoRoute(path: '/sync-status', builder: (context, state) => const SyncStatusScreen()),
    GoRoute(
      path: '/shipments/:id/recommendation',
      builder: (context, state) => RecommendationScreen(
        shipmentId: state.pathParameters['id']!,
        args: state.extra as RecommendationArgs?,
      ),
    ),
    GoRoute(path: '/notifications', builder: (context, state) => const NotificationsScreen()),
    GoRoute(path: '/driver/manifest', builder: (context, state) => const DriverManifestScreen()),
    GoRoute(
      path: '/driver/stops/:id',
      builder: (context, state) => StopDetailScreen(
        stopId: state.pathParameters['id']!,
        stop: state.extra as ManifestStop?,
      ),
    ),
    GoRoute(path: '/settings', builder: (context, state) => const SettingsScreen()),
  ],
);
