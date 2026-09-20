import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../theme/fresh_supplies_colors.dart';
import 'risk_tier_badge.dart';

/// Driver-density list row for Screen 8 (manifest). Render exactly what the
/// manifest endpoint returns per stop — cooperative pickups are already
/// grouped server-side into one stop per collection point; do not fragment
/// further client-side.
class StopTile extends StatelessWidget {
  final int sequence;
  final String collectionPointName;
  final String crop;
  final double quantityKg;
  final RiskTier? riskTier;
  final VoidCallback onTap;

  const StopTile({
    super.key,
    required this.sequence,
    required this.collectionPointName,
    required this.crop,
    required this.quantityKg,
    required this.riskTier,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(AppRadius.lg),
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.md),
        margin: const EdgeInsets.only(bottom: AppSpacing.sm),
        decoration: BoxDecoration(
          color: colors.card,
          borderRadius: BorderRadius.circular(AppRadius.lg),
          border: Border.all(color: colors.border),
        ),
        child: Row(
          children: [
            CircleAvatar(
              radius: 16,
              backgroundColor: colors.muted,
              child: Text('$sequence', style: TextStyle(color: colors.mutedForeground, fontWeight: FontWeight.w600)),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(collectionPointName, style: TextStyle(color: colors.foreground, fontWeight: FontWeight.w600, fontSize: 15)),
                  const SizedBox(height: 2),
                  Text('$crop · ${quantityKg.toStringAsFixed(0)} kg', style: TextStyle(color: colors.mutedForeground, fontSize: 13)),
                ],
              ),
            ),
            if (riskTier != null) RiskTierBadge(tier: riskTier!, small: true),
            const SizedBox(width: AppSpacing.xs),
            Icon(Icons.chevron_right, color: colors.mutedForeground),
          ],
        ),
      ),
    );
  }
}
