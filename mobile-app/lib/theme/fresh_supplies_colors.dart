import 'package:flutter/material.dart';

/// Design tokens mirrored 1:1 from the web app's Tailwind v4 CSS variables
/// in `src/app/globals.css` (`:root` = light, `.dark` = dark). Do not invent
/// new colors here — if a value is needed that isn't below, go re-read
/// globals.css rather than guessing.
///
/// riskFresh / riskAtRisk / riskCritical are NOT separate CSS variables on
/// the web app today — RiskTierBadge (src/components/shipments/risk-tier-
/// badge.tsx) maps Fresh -> the shared Badge's "default" variant (primary),
/// At-Risk -> "warning", Critical -> "destructive" (see badgeVariants in
/// src/components/ui/badge.tsx). They're formalized here as their own named
/// tokens for the mobile app's convenience, but they are exactly equal to
/// primary/warning/destructive — flagging this back per the build spec:
/// the web app would benefit from promoting these to real --risk-* CSS
/// variables so both apps read from one named source instead of this
/// mobile app re-deriving the mapping.
class FreshSuppliesColors extends ThemeExtension<FreshSuppliesColors> {
  final Color background;
  final Color foreground;
  final Color card;
  final Color cardForeground;
  final Color primary;
  final Color primaryForeground;
  final Color secondary;
  final Color secondaryForeground;
  final Color muted;
  final Color mutedForeground;
  final Color accent;
  final Color accentForeground;
  final Color destructive;
  final Color destructiveForeground;
  final Color success;
  final Color successForeground;
  final Color warning;
  final Color warningForeground;
  final Color border;
  final Color input;
  final Color ring;

  // Risk-tier tokens — equal to primary/warning/destructive, see class doc.
  final Color riskFresh;
  final Color riskFreshForeground;
  final Color riskAtRisk;
  final Color riskAtRiskForeground;
  final Color riskCritical;
  final Color riskCriticalForeground;

  const FreshSuppliesColors({
    required this.background,
    required this.foreground,
    required this.card,
    required this.cardForeground,
    required this.primary,
    required this.primaryForeground,
    required this.secondary,
    required this.secondaryForeground,
    required this.muted,
    required this.mutedForeground,
    required this.accent,
    required this.accentForeground,
    required this.destructive,
    required this.destructiveForeground,
    required this.success,
    required this.successForeground,
    required this.warning,
    required this.warningForeground,
    required this.border,
    required this.input,
    required this.ring,
    required this.riskFresh,
    required this.riskFreshForeground,
    required this.riskAtRisk,
    required this.riskAtRiskForeground,
    required this.riskCritical,
    required this.riskCriticalForeground,
  });

  /// `:root` values in src/app/globals.css.
  static const light = FreshSuppliesColors(
    background: Color(0xFFF5F7F5),
    foreground: Color(0xFF12201A),
    card: Color(0xFFFFFFFF),
    cardForeground: Color(0xFF12201A),
    primary: Color(0xFF1F6F4A),
    primaryForeground: Color(0xFFF7FBF8),
    secondary: Color(0xFFE7ECE8),
    secondaryForeground: Color(0xFF14201A),
    muted: Color(0xFFEAEEEA),
    mutedForeground: Color(0xFF5B6B60),
    accent: Color(0xFFE8A33D),
    accentForeground: Color(0xFF201404),
    destructive: Color(0xFFC4432B),
    destructiveForeground: Color(0xFFFFF7F2),
    success: Color(0xFF2E8B5B),
    successForeground: Color(0xFFF2FBF6),
    warning: Color(0xFFE8A33D),
    warningForeground: Color(0xFF241705),
    border: Color(0xFFDCE3DE),
    input: Color(0xFFDCE3DE),
    ring: Color(0xFF1F6F4A),
    riskFresh: Color(0xFF1F6F4A), // == primary
    riskFreshForeground: Color(0xFFF7FBF8),
    riskAtRisk: Color(0xFFE8A33D), // == warning
    riskAtRiskForeground: Color(0xFF241705),
    riskCritical: Color(0xFFC4432B), // == destructive
    riskCriticalForeground: Color(0xFFFFF7F2),
  );

  /// `.dark` values in src/app/globals.css.
  static const dark = FreshSuppliesColors(
    background: Color(0xFF0E1512),
    foreground: Color(0xFFE7EDE8),
    card: Color(0xFF131C17),
    cardForeground: Color(0xFFE7EDE8),
    primary: Color(0xFF3FA372),
    primaryForeground: Color(0xFF0B1410),
    secondary: Color(0xFF1B2620),
    secondaryForeground: Color(0xFFE7EDE8),
    muted: Color(0xFF1B2620),
    mutedForeground: Color(0xFF93A69B),
    accent: Color(0xFFF0B458),
    accentForeground: Color(0xFF241705),
    destructive: Color(0xFFE2634A),
    destructiveForeground: Color(0xFF2A0B04),
    success: Color(0xFF3FA372),
    successForeground: Color(0xFF0B1410),
    warning: Color(0xFFF0B458),
    warningForeground: Color(0xFF241705),
    border: Color(0xFF223027),
    input: Color(0xFF223027),
    ring: Color(0xFF3FA372),
    riskFresh: Color(0xFF3FA372), // == primary
    riskFreshForeground: Color(0xFF0B1410),
    riskAtRisk: Color(0xFFF0B458), // == warning
    riskAtRiskForeground: Color(0xFF241705),
    riskCritical: Color(0xFFE2634A), // == destructive
    riskCriticalForeground: Color(0xFF2A0B04),
  );

  @override
  FreshSuppliesColors copyWith({
    Color? background,
    Color? foreground,
    Color? card,
    Color? cardForeground,
    Color? primary,
    Color? primaryForeground,
    Color? secondary,
    Color? secondaryForeground,
    Color? muted,
    Color? mutedForeground,
    Color? accent,
    Color? accentForeground,
    Color? destructive,
    Color? destructiveForeground,
    Color? success,
    Color? successForeground,
    Color? warning,
    Color? warningForeground,
    Color? border,
    Color? input,
    Color? ring,
    Color? riskFresh,
    Color? riskFreshForeground,
    Color? riskAtRisk,
    Color? riskAtRiskForeground,
    Color? riskCritical,
    Color? riskCriticalForeground,
  }) {
    return FreshSuppliesColors(
      background: background ?? this.background,
      foreground: foreground ?? this.foreground,
      card: card ?? this.card,
      cardForeground: cardForeground ?? this.cardForeground,
      primary: primary ?? this.primary,
      primaryForeground: primaryForeground ?? this.primaryForeground,
      secondary: secondary ?? this.secondary,
      secondaryForeground: secondaryForeground ?? this.secondaryForeground,
      muted: muted ?? this.muted,
      mutedForeground: mutedForeground ?? this.mutedForeground,
      accent: accent ?? this.accent,
      accentForeground: accentForeground ?? this.accentForeground,
      destructive: destructive ?? this.destructive,
      destructiveForeground: destructiveForeground ?? this.destructiveForeground,
      success: success ?? this.success,
      successForeground: successForeground ?? this.successForeground,
      warning: warning ?? this.warning,
      warningForeground: warningForeground ?? this.warningForeground,
      border: border ?? this.border,
      input: input ?? this.input,
      ring: ring ?? this.ring,
      riskFresh: riskFresh ?? this.riskFresh,
      riskFreshForeground: riskFreshForeground ?? this.riskFreshForeground,
      riskAtRisk: riskAtRisk ?? this.riskAtRisk,
      riskAtRiskForeground: riskAtRiskForeground ?? this.riskAtRiskForeground,
      riskCritical: riskCritical ?? this.riskCritical,
      riskCriticalForeground: riskCriticalForeground ?? this.riskCriticalForeground,
    );
  }

  @override
  FreshSuppliesColors lerp(ThemeExtension<FreshSuppliesColors>? other, double t) {
    if (other is! FreshSuppliesColors) return this;
    Color l(Color a, Color b) => Color.lerp(a, b, t)!;
    return FreshSuppliesColors(
      background: l(background, other.background),
      foreground: l(foreground, other.foreground),
      card: l(card, other.card),
      cardForeground: l(cardForeground, other.cardForeground),
      primary: l(primary, other.primary),
      primaryForeground: l(primaryForeground, other.primaryForeground),
      secondary: l(secondary, other.secondary),
      secondaryForeground: l(secondaryForeground, other.secondaryForeground),
      muted: l(muted, other.muted),
      mutedForeground: l(mutedForeground, other.mutedForeground),
      accent: l(accent, other.accent),
      accentForeground: l(accentForeground, other.accentForeground),
      destructive: l(destructive, other.destructive),
      destructiveForeground: l(destructiveForeground, other.destructiveForeground),
      success: l(success, other.success),
      successForeground: l(successForeground, other.successForeground),
      warning: l(warning, other.warning),
      warningForeground: l(warningForeground, other.warningForeground),
      border: l(border, other.border),
      input: l(input, other.input),
      ring: l(ring, other.ring),
      riskFresh: l(riskFresh, other.riskFresh),
      riskFreshForeground: l(riskFreshForeground, other.riskFreshForeground),
      riskAtRisk: l(riskAtRisk, other.riskAtRisk),
      riskAtRiskForeground: l(riskAtRiskForeground, other.riskAtRiskForeground),
      riskCritical: l(riskCritical, other.riskCritical),
      riskCriticalForeground: l(riskCriticalForeground, other.riskCriticalForeground),
    );
  }
}

extension FreshSuppliesColorsContext on BuildContext {
  FreshSuppliesColors get colors => Theme.of(this).extension<FreshSuppliesColors>()!;
}
