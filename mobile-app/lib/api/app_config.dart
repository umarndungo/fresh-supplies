/// Backend base URL. There is deliberately no hardcoded fallback pointing at
/// a live host: the deployed backend now sits behind a single Cloudflare
/// Tunnel (see docker-compose.yml's `cloudflared` service and the Caddyfile)
/// whose hostname is a free "quick tunnel" URL that changes whenever that
/// container restarts — baking today's URL in as a default just reproduces
/// the same stale-URL problem this replaced.
///
/// Always pass the current one at build time:
/// `--dart-define=API_BASE_URL=https://<current>.trycloudflare.com/api/v1`
/// (get `<current>` from `docker compose logs cloudflared` on the deploy
/// box). Once a real domain is in the picture, a named tunnel gives this a
/// fixed hostname and this override becomes a one-time value instead of a
/// per-restart one.
///
/// Falling back to a syntactically-valid-but-unreachable placeholder (rather
/// than throwing) matters for `flutter test`'s widget smoke tests, which
/// boot the real app — and therefore construct [ApiClient] — without ever
/// passing this define; they never make a real request, so there's nothing
/// for a live default to protect them against. A real build made without
/// the define now fails loudly with connection errors against
/// `unconfigured.invalid` instead of silently hitting a stale dead tunnel.
class AppConfig {
  AppConfig._();

  static const _override = String.fromEnvironment('API_BASE_URL');
  static const _unconfigured = 'https://unconfigured.invalid/api/v1';

  static String get apiBaseUrl => _override.isNotEmpty ? _override : _unconfigured;
}
