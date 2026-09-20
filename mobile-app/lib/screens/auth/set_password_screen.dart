import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../api/api_client.dart';
import '../../api/mobile_auth_api.dart';
import '../../auth/auth_controller.dart';
import '../../theme/app_theme.dart';
import '../../theme/fresh_supplies_colors.dart';
import '../../widgets/app_text_field.dart';
import '../../widgets/primary_button.dart';

/// First-login step for a top-down provisioned account (admin or
/// cooperative admin added you — see backend/docs/multitenancy_design.md).
/// Route: /auth/set-password. Full name/role/cooperative are already set by
/// whoever provisioned the account, so all that's left is choosing a
/// password for future logins (this OTP-verified session is proof enough of
/// email ownership).
class SetPasswordScreen extends StatefulWidget {
  const SetPasswordScreen({super.key});

  @override
  State<SetPasswordScreen> createState() => _SetPasswordScreenState();
}

class _SetPasswordScreenState extends State<SetPasswordScreen> {
  final _authApi = MobileAuthApi();
  final _passwordController = TextEditingController();
  final _confirmController = TextEditingController();
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _passwordController.dispose();
    _confirmController.dispose();
    super.dispose();
  }

  bool get _canContinue => _passwordController.text.length >= 8;

  Future<void> _continue() async {
    final password = _passwordController.text;
    if (password.length < 8) {
      setState(() => _error = 'Password must be at least 8 characters.');
      return;
    }
    if (password != _confirmController.text) {
      setState(() => _error = 'Passwords do not match.');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await _authApi.setPassword(password);
      await AuthController.instance.onProfileCompleted();
      if (!mounted) return;
      context.go('/home');
    } catch (e) {
      if (!mounted) return;
      final message = e is ApiException ? e.message : "Couldn't save — check your connection and try again.";
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
          padding: const EdgeInsets.all(AppSpacing.xl),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Set your password',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: colors.foreground),
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(
                "You're signed in — choose a password so you can sign in directly next time.",
                style: TextStyle(fontSize: 14, color: colors.mutedForeground),
              ),
              const SizedBox(height: AppSpacing.xl),
              AppTextField(
                label: 'New password',
                hint: '••••••••',
                controller: _passwordController,
                obscureText: true,
                onChanged: (_) => setState(() {}),
              ),
              const SizedBox(height: AppSpacing.lg),
              AppTextField(
                label: 'Confirm password',
                hint: '••••••••',
                controller: _confirmController,
                obscureText: true,
                onChanged: (_) => setState(() {}),
              ),
              if (_error != null) ...[
                const SizedBox(height: AppSpacing.md),
                Text(_error!, style: TextStyle(color: colors.destructive)),
              ],
              const Spacer(),
              PrimaryButton(
                label: 'Set password',
                loading: _loading,
                onPressed: _canContinue ? _continue : null,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
