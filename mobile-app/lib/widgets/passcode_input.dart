import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../theme/fresh_supplies_colors.dart';

/// 6-box OTP entry filled by a custom on-screen keypad (not the OS keyboard)
/// — per the build spec's "branded-PIN-entry pattern" for Screen 2. Purely
/// presentational + input collection; the caller owns submit/resend/timer
/// logic.
class PasscodeInput extends StatefulWidget {
  final int length;
  final ValueChanged<String> onCompleted;
  final ValueChanged<String>? onChanged;

  const PasscodeInput({super.key, this.length = 6, required this.onCompleted, this.onChanged});

  @override
  State<PasscodeInput> createState() => _PasscodeInputState();
}

class _PasscodeInputState extends State<PasscodeInput> {
  String _value = '';

  void _append(String digit) {
    if (_value.length >= widget.length) return;
    setState(() => _value += digit);
    widget.onChanged?.call(_value);
    if (_value.length == widget.length) widget.onCompleted(_value);
  }

  void _backspace() {
    if (_value.isEmpty) return;
    setState(() => _value = _value.substring(0, _value.length - 1));
    widget.onChanged?.call(_value);
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(widget.length, (i) {
            final filled = i < _value.length;
            return Container(
              margin: const EdgeInsets.symmetric(horizontal: AppSpacing.xs),
              width: 44,
              height: 52,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: colors.card,
                borderRadius: BorderRadius.circular(AppRadius.md),
                border: Border.all(color: filled ? colors.ring : colors.border, width: filled ? 2 : 1),
              ),
              child: Text(
                filled ? '•' : '',
                style: TextStyle(fontSize: 24, color: colors.foreground, fontWeight: FontWeight.bold),
              ),
            );
          }),
        ),
        const SizedBox(height: AppSpacing.xl),
        _Keypad(onDigit: _append, onBackspace: _backspace),
      ],
    );
  }
}

class _Keypad extends StatelessWidget {
  final ValueChanged<String> onDigit;
  final VoidCallback onBackspace;

  const _Keypad({required this.onDigit, required this.onBackspace});

  static const _rows = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['', '0', 'back'],
  ];

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: _rows
          .map(
            (row) => Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: row.map((key) {
                if (key.isEmpty) return const SizedBox(width: 72, height: 56);
                final isBackspace = key == 'back';
                return SizedBox(
                  width: 72,
                  height: 56,
                  child: TextButton(
                    onPressed: isBackspace ? onBackspace : () => onDigit(key),
                    child: isBackspace
                        ? Icon(Icons.backspace_outlined, color: colors.mutedForeground)
                        : Text(key, style: TextStyle(fontSize: 24, color: colors.foreground)),
                  ),
                );
              }).toList(),
            ),
          )
          .toList(),
    );
  }
}
