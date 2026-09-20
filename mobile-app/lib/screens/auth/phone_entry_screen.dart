import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../api/api_client.dart';
import '../../api/mobile_auth_api.dart';
import '../../theme/app_theme.dart';
import '../../theme/fresh_supplies_colors.dart';
import '../../widgets/app_text_field.dart';
import '../../widgets/primary_button.dart';

final _emailPattern = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');

/// Screen 1 — Email Entry / OTP Request. Route: /auth/email.
/// Entry point to auth; no password anywhere in this flow — login is by
/// emailed one-time code (switched from phone/SMS OTP; see
/// backend/app/core/email_sender.py).
class PhoneEntryScreen extends StatefulWidget {
  const PhoneEntryScreen({super.key});

  @override
  State<PhoneEntryScreen> createState() => _PhoneEntryScreenState();
}

class _PhoneEntryScreenState extends State<PhoneEntryScreen> {
  final _controller = TextEditingController();
  final _authApi = MobileAuthApi();
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _sendCode() async {
    final email = _controller.text.trim();
    if (!_emailPattern.hasMatch(email)) {
      setState(() => _error = 'Enter a valid email address.');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await _authApi.requestOtp(email);
      if (!mounted) return;
      context.push('/auth/verify', extra: email);
    } catch (e) {
      if (!mounted) return;
      // 404 = no account exists for this email — every account is now
      // provisioned top-down by an admin/cooperative admin (see
      // MobileAuthApi's doc comment), so surface that message directly
      // rather than a generic "try again".
      final message = e is ApiException && e.statusCode == 404
          ? e.message
          : "Couldn't send code, try again.";
      setState(() => _error = message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xl),
          child: Column(
            children: [
              const Spacer(flex: 2),
              Text(
                'Fresh Supplies',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: colors.primary),
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(
                'Welcome to Fresh Supplies',
                style: TextStyle(fontSize: 16, color: colors.mutedForeground),
              ),
              const Spacer(flex: 1),
              AppTextField(
                label: 'Email address',
                hint: 'you@example.com',
                controller: _controller,
                keyboardType: TextInputType.emailAddress,
                errorText: _error,
                prefix: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
                  child: Icon(Icons.mail_outline, color: colors.mutedForeground, size: 20),
                ),
              ),
              const SizedBox(height: AppSpacing.lg),
              PrimaryButton(label: 'Send code', loading: _loading, onPressed: _sendCode),
              const Spacer(flex: 3),
            ],
          ),
        ),
      ),
    );
  }
}
