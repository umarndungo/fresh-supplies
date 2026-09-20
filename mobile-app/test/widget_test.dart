// Smoke tests: the app boots into the auth chain and the theme applies in
// both light and dark. Screen-specific tests live alongside future work as
// each screen gets wired to a real backend in Phase 5.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mobile_app/main.dart';

void main() {
  testWidgets('App boots to email entry (initial route)', (WidgetTester tester) async {
    await tester.pumpWidget(const FreshSuppliesApp());
    await tester.pumpAndSettle();

    expect(find.text('Fresh Supplies'), findsWidgets);
    expect(find.text('Send code'), findsOneWidget);
  });

  testWidgets('Dark theme applies without error', (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(400, 800));
    tester.platformDispatcher.platformBrightnessTestValue = Brightness.dark;
    await tester.pumpWidget(const FreshSuppliesApp());
    await tester.pumpAndSettle();

    expect(find.byType(MaterialApp), findsOneWidget);
    tester.platformDispatcher.clearPlatformBrightnessTestValue();
  });
}
