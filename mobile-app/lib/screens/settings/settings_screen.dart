import 'package:flutter/material.dart';

import '../../api/language_store.dart';
import '../../auth/auth_controller.dart';
import '../../theme/app_theme.dart';
import '../../theme/fresh_supplies_colors.dart';
import '../../widgets/app_bottom_nav.dart';

/// Screen 10 — Settings / Language. Route: /settings.
/// Shared between roles. Density: minimal.
///
/// The language toggle here is real, not visual-only: LanguageStore is read
/// by ApiClient on every request and sent as Accept-Language (see
/// api/language_store.dart), so risk labels and recommendation sentences —
/// which are server-driven copy per the build spec — actually come back
/// translated once the backend's i18n has Swahili copy for a given key.
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late String _language = LanguageStore.instance.current == 'sw' ? 'Kiswahili' : 'English';
  bool _notificationsEnabled = true;

  // No phone number shown here: there's no "GET /mobile/auth/me" endpoint to
  // re-fetch account details on a fresh app start, and TokenStore only
  // persists what routing needs (role, profile-completed) — not the phone
  // number from the one-time OTP-verify response. Real fix is a small
  // backend addition; flagged rather than threading it through by hand.

  Future<void> _confirmLogout() async {
    final colors = context.colors;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: colors.card,
        title: Text('Log out?', style: TextStyle(color: colors.foreground)),
        content: Text('You can log back in with your phone number any time.', style: TextStyle(color: colors.mutedForeground)),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text('Cancel')),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: Text('Log out', style: TextStyle(color: colors.destructive)),
          ),
        ],
      ),
    );
    // No explicit navigation needed — AuthController is the router's
    // refreshListenable, so logging out triggers the redirect to
    // /auth/phone on its own.
    if (confirmed == true) await AuthController.instance.logout();
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      bottomNavigationBar: const AppBottomNav(currentIndex: 3),
      body: ListView(
        children: [
          const _SectionLabel('Account'),
          ListTile(
            leading: Icon(Icons.person_outline, color: colors.mutedForeground),
            title: Text('Phone number', style: TextStyle(color: colors.foreground)),
            subtitle: Text('Signed in', style: TextStyle(color: colors.mutedForeground)),
          ),
          Divider(height: 1, color: colors.border),
          const _SectionLabel('Preferences'),
          ListTile(
            leading: Icon(Icons.language_outlined, color: colors.mutedForeground),
            title: Text('Language', style: TextStyle(color: colors.foreground)),
            trailing: DropdownButton<String>(
              value: _language,
              underline: const SizedBox.shrink(),
              items: const [
                DropdownMenuItem(value: 'English', child: Text('English')),
                DropdownMenuItem(value: 'Kiswahili', child: Text('Kiswahili')),
              ],
              onChanged: (v) async {
                if (v == null) return;
                setState(() => _language = v);
                await LanguageStore.instance.set(v == 'Kiswahili' ? 'sw' : 'en');
              },
            ),
          ),
          SwitchListTile(
            secondary: Icon(Icons.notifications_outlined, color: colors.mutedForeground),
            title: Text('Notifications', style: TextStyle(color: colors.foreground)),
            value: _notificationsEnabled,
            activeThumbColor: colors.primary,
            onChanged: (v) => setState(() => _notificationsEnabled = v),
          ),
          Divider(height: 1, color: colors.border),
          const SizedBox(height: AppSpacing.lg),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
            child: OutlinedButton(
              onPressed: _confirmLogout,
              style: OutlinedButton.styleFrom(foregroundColor: colors.destructive, side: BorderSide(color: colors.destructive)),
              child: const Text('Log out'),
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String text;
  const _SectionLabel(this.text);

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return Padding(
      padding: const EdgeInsets.fromLTRB(AppSpacing.lg, AppSpacing.lg, AppSpacing.lg, AppSpacing.xs),
      child: Text(text.toUpperCase(), style: TextStyle(color: colors.mutedForeground, fontSize: 12, fontWeight: FontWeight.w600, letterSpacing: 0.5)),
    );
  }
}
