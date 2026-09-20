import 'package:flutter/material.dart';

import 'api/api_client.dart';
import 'api/language_store.dart';
import 'auth/auth_controller.dart';
import 'offline/offline_queue.dart';
import 'router.dart';
import 'theme/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Each of these is independently defensive: a platform without working
  // local storage shouldn't leave the user staring at a blank screen with
  // no route ever matching — better to boot logged-out than not boot at all.
  try {
    await LanguageStore.instance.load();
  } catch (_) {}
  try {
    await OfflineQueue.instance.load();
  } catch (_) {}
  await AuthController.instance.bootstrap(); // has its own internal fallback
  // A failed silent refresh (expired/revoked refresh token) logs the user
  // out; AuthController is the router's refreshListenable, so this alone
  // is enough to redirect to /auth/phone.
  ApiClient.instance.onSessionExpired = () => AuthController.instance.logout();
  runApp(const FreshSuppliesApp());
}

/// Root widget. Screens are wired to the real backend per Phase 5 (see
/// router.dart's redirect logic and each screen's API calls) — Phase 4's
/// mock data only remains for Notifications (Screen 7), since no backend
/// endpoint for notifications exists yet in the mobile API contract.
class FreshSuppliesApp extends StatelessWidget {
  const FreshSuppliesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Fresh Supplies',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: ThemeMode.system,
      routerConfig: appRouter,
    );
  }
}
