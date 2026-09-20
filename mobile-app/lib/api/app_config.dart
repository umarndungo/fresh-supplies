import 'dart:io' show Platform;

import 'package:flutter/foundation.dart' show kIsWeb;

/// Backend base URL. The Android emulator can't reach the host's
/// `localhost` directly — it must use the special `10.0.2.2` alias — so this
/// picks the right default per platform. Override at build time with
/// `--dart-define=API_BASE_URL=https://your-host/api/v1` for a real device,
/// a Cloudflare tunnel (see the docker-compose/CORS work earlier in this
/// project), or a staging server.
class AppConfig {
  AppConfig._();

  static const _override = String.fromEnvironment('API_BASE_URL');

  static String get apiBaseUrl {
    if (_override.isNotEmpty) return _override;
    if (kIsWeb) return 'http://localhost:8000/api/v1';
    if (Platform.isAndroid) return 'http://10.0.2.2:8000/api/v1';
    return 'http://localhost:8000/api/v1';
  }
}
