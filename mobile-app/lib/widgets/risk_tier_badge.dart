import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../theme/fresh_supplies_colors.dart';

/// Mirrors the web app's risk tiers exactly — see src/types/ml.types.ts and
/// src/components/shipments/risk-tier-badge.tsx (Fresh/At-Risk/Critical,
/// title case; backend sends FRESH/AT_RISK/CRITICAL, normalized there).
enum RiskTier { fresh, atRisk, critical }

RiskTier? riskTierFromApi(String raw) {
  switch (raw.trim().toUpperCase().replaceAll(RegExp(r'[\s-]+'), '_')) {
    case 'FRESH':
      return RiskTier.fresh;
    case 'AT_RISK':
      return RiskTier.atRisk;
    case 'CRITICAL':
      return RiskTier.critical;
    default:
      return null;
  }
}

/// The one shared risk-tier pill, used identically everywhere a shipment's
/// risk tier is shown. Label text is a static UI label (not server copy —
/// the server-driven recommendation *sentence* is separate, see Screen 6).
class RiskTierBadge extends StatelessWidget {
  final RiskTier tier;

  /// Driver screens (manifest list) use a smaller variant than the large,
  /// centered badge on the farmer Recommendation screen.
  final bool small;

  const RiskTierBadge({super.key, required this.tier, this.small = false});

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final (bg, fg, label) = switch (tier) {
      RiskTier.fresh => (colors.riskFresh, colors.riskFreshForeground, 'Fresh'),
      RiskTier.atRisk => (colors.riskAtRisk, colors.riskAtRiskForeground, 'At-Risk'),
      RiskTier.critical => (colors.riskCritical, colors.riskCriticalForeground, 'Critical'),
    };
    return Container(
      padding: EdgeInsets.symmetric(horizontal: small ? AppSpacing.sm : AppSpacing.lg, vertical: small ? 2 : AppSpacing.xs),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(AppRadius.pill)),
      child: Text(
        label,
        style: TextStyle(color: fg, fontWeight: FontWeight.w600, fontSize: small ? 12 : 16),
      ),
    );
  }
}
