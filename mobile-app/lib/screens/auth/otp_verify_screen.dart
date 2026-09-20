import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../api/device_api.dart';
import '../../api/mobile_auth_api.dart';
import '../../auth/auth_controller.dart';
import '../../theme/app_theme.dart';
import '../../theme/fresh_supplies_colors.dart';
import '../../widgets/passcode_input.dart';

/// Screen 2 — OTP Verification. Route: /auth/verify.
class OtpVerifyScreen extends StatefulWidget {
  final String email;

  const OtpVerifyScreen({super.key, required this.email});

  @override
  State<OtpVerifyScreen> createState() => _OtpVerifyScreenState();
}

class _OtpVerifyScreenState extends State<OtpVerifyScreen> {
  final _authApi = MobileAuthApi();
  int _resendCooldown = 30;
  Timer? _timer;
  bool _verifying = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _startCooldown();
  }

  void _startCooldown() {
    _timer?.cancel();
    setState(() => _resendCooldown = 30);
    _timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (_resendCooldown <= 1) {
        t.cancel();
        setState(() => _resendCooldown = 0);
      } else {
        setState(() => _resendCooldown -= 1);
      }
    });
  }

  Future<void> _resend() async {
    try {
      await _authApi.requestOtp(widget.email);
    } catch (_) {
      // Silent — the countdown restarting is feedback enough; a failed
      // resend just means the user can try the button again once it re-enables.
    }
    _startCooldown();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _onCompleted(String code) async {
    setState(() {
      _verifying = true;
      _error = null;
    });
    try {
      final tokens = await _authApi.verifyOtp(widget.email, code);
      await AuthController.instance.onOtpVerified(tokens);
      // Best-effort device registration — no real push provider wired up
      // yet (see DeviceApi's doc comment), just exercising the endpoint.
      unawaited(DeviceApi().registerDevice(token: 'placeholder-${tokens.user.id}', platform: 'android').catchError((_) {}));
      if (!mounted) return;
      context.go(tokens.user.profileCompleted ? '/home' : '/auth/set-password');
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _verifying = false;
        _error = 'Incorrect code — try again.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return Scaffold(
      appBar: AppBar(leading: BackButton(onPressed: () => context.pop())),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xl),
          child: Column(
            children: [
              const SizedBox(height: AppSpacing.xl),
              Text(
                'Enter the 6-digit code sent to\n${widget.email}',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: colors.foreground),
              ),
              const SizedBox(height: AppSpacing.xxl),
              if (_verifying)
                const CircularProgressIndicator()
              else
                PasscodeInput(key: ValueKey(_error), onCompleted: _onCompleted),
              if (_error != null) ...[
                const SizedBox(height: AppSpacing.md),
                Text(_error!, style: TextStyle(color: colors.destructive)),
              ],
              const SizedBox(height: AppSpacing.xl),
              TextButton(
                onPressed: _resendCooldown == 0 ? _resend : null,
                child: Text(
                  _resendCooldown == 0 ? 'Resend code' : 'Resend code in ${_resendCooldown}s',
                  style: TextStyle(color: _resendCooldown == 0 ? colors.primary : colors.mutedForeground),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
