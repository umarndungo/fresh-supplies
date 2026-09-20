import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../theme/fresh_supplies_colors.dart';

enum ViewState { loading, empty, error, content }

/// The three states every screen must handle (per the build spec's global
/// conventions), plus the happy path, in one place so each screen doesn't
/// re-invent loading spinners / empty copy / retry buttons.
class AsyncStateView extends StatelessWidget {
  final ViewState state;
  final Widget content;
  final String emptyMessage;
  final String errorMessage;
  final VoidCallback? onRetry;

  const AsyncStateView({
    super.key,
    required this.state,
    required this.content,
    this.emptyMessage = 'Nothing here yet.',
    this.errorMessage = "Couldn't load — check your connection.",
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    switch (state) {
      case ViewState.loading:
        return const Center(child: CircularProgressIndicator());
      case ViewState.empty:
        return _Message(text: emptyMessage, colors: context.colors);
      case ViewState.error:
        return _Message(text: errorMessage, colors: context.colors, onRetry: onRetry);
      case ViewState.content:
        return content;
    }
  }
}

class _Message extends StatelessWidget {
  final String text;
  final FreshSuppliesColors colors;
  final VoidCallback? onRetry;

  const _Message({required this.text, required this.colors, this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(text, textAlign: TextAlign.center, style: TextStyle(color: colors.mutedForeground, fontSize: 15)),
            if (onRetry != null) ...[
              const SizedBox(height: AppSpacing.md),
              TextButton(onPressed: onRetry, child: const Text('Retry')),
            ],
          ],
        ),
      ),
    );
  }
}
