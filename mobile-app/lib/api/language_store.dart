import 'package:shared_preferences/shared_preferences.dart';

/// The user's language choice, sent as Accept-Language on every request per
/// the build spec: "server-driven copy ... comes from the API response (per
/// Accept-Language), not hardcoded strings." Screen 10's toggle writes here;
/// ApiClient reads it on every request.
class LanguageStore {
  LanguageStore._();
  static final LanguageStore instance = LanguageStore._();

  static const _key = 'accept_language';

  String _current = 'en';
  String get current => _current;

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    _current = prefs.getString(_key) ?? 'en';
  }

  Future<void> set(String languageCode) async {
    _current = languageCode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, languageCode);
  }
}
