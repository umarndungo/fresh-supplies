import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../theme/fresh_supplies_colors.dart';

/// The one shared text input. Wraps Material's TextField/TextFormField with
/// the app's token-driven decoration (see AppTheme.inputDecorationTheme) plus
/// a label above the field, which the web app's form fields use consistently.
class AppTextField extends StatelessWidget {
  final String? label;
  final String? hint;
  final TextEditingController? controller;
  final TextInputType? keyboardType;
  final int maxLines;
  final Widget? prefix;
  final String? errorText;
  final ValueChanged<String>? onChanged;
  final bool obscureText;

  const AppTextField({
    super.key,
    this.label,
    this.hint,
    this.controller,
    this.keyboardType,
    this.maxLines = 1,
    this.prefix,
    this.errorText,
    this.onChanged,
    this.obscureText = false,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label != null) ...[
          Text(label!, style: TextStyle(color: colors.mutedForeground, fontSize: 14, fontWeight: FontWeight.w500)),
          const SizedBox(height: AppSpacing.xs),
        ],
        TextField(
          controller: controller,
          keyboardType: keyboardType,
          maxLines: obscureText ? 1 : maxLines,
          obscureText: obscureText,
          onChanged: onChanged,
          style: TextStyle(color: colors.foreground, fontSize: 16),
          decoration: InputDecoration(hintText: hint, prefixIcon: prefix, errorText: errorText),
        ),
      ],
    );
  }
}
