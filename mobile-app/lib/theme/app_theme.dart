import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'fresh_supplies_colors.dart';

/// Border radius scale, derived from --radius: 0.75rem (12px) in
/// src/app/globals.css: --radius-sm = radius-4px, --radius-md = radius-2px,
/// --radius-lg = radius, --radius-xl = radius+4px.
class AppRadius {
  static const sm = 8.0;
  static const md = 10.0;
  static const lg = 12.0;
  static const xl = 16.0;
  static const pill = 999.0; // pill-shaped buttons/badges, observed in the deployed UI
}

/// Spacing scale — Tailwind's default 4px base unit, as used throughout src/.
class AppSpacing {
  static const xs = 4.0;
  static const sm = 8.0;
  static const md = 12.0;
  static const lg = 16.0;
  static const xl = 24.0;
  static const xxl = 32.0;
}

class AppTheme {
  AppTheme._();

  // src/app/layout.tsx: Manrope (sans) + IBM Plex Mono (mono).
  static TextTheme _textTheme(Color color) =>
      GoogleFonts.manropeTextTheme().apply(bodyColor: color, displayColor: color);

  static ThemeData light() => _build(FreshSuppliesColors.light, Brightness.light);
  static ThemeData dark() => _build(FreshSuppliesColors.dark, Brightness.dark);

  static ThemeData _build(FreshSuppliesColors colors, Brightness brightness) {
    final colorScheme = ColorScheme(
      brightness: brightness,
      primary: colors.primary,
      onPrimary: colors.primaryForeground,
      secondary: colors.secondary,
      onSecondary: colors.secondaryForeground,
      error: colors.destructive,
      onError: colors.destructiveForeground,
      surface: colors.card,
      onSurface: colors.cardForeground,
    );

    return ThemeData(
      brightness: brightness,
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: colors.background,
      textTheme: _textTheme(colors.foreground),
      dividerColor: colors.border,
      extensions: [colors],
      appBarTheme: AppBarTheme(
        backgroundColor: colors.background,
        foregroundColor: colors.foreground,
        elevation: 0,
        scrolledUnderElevation: 0,
      ),
      cardTheme: CardThemeData(
        color: colors.card,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.lg),
          side: BorderSide(color: colors.border),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: colors.card,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
          borderSide: BorderSide(color: colors.border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
          borderSide: BorderSide(color: colors.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppRadius.md),
          borderSide: BorderSide(color: colors.ring, width: 2),
        ),
        hintStyle: TextStyle(color: colors.mutedForeground),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: colors.primary,
          foregroundColor: colors.primaryForeground,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.pill)),
          padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
          textStyle: GoogleFonts.manrope(fontWeight: FontWeight.w600, fontSize: 16),
        ),
      ),
    );
  }
}
