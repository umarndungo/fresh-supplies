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
class AppConfig {
  AppConfig._();

  static const _override = String.fromEnvironment('API_BASE_URL');

  static String get apiBaseUrl {
    if (_override.isEmpty) {
      throw StateError(
        'API_BASE_URL was not set. Build with '
        '--dart-define=API_BASE_URL=https://<current-tunnel-host>/api/v1 '
        '(see docker compose logs cloudflared on the deploy box).',
      );
    }
    return _override;
  }
}
