import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../theme/fresh_supplies_colors.dart';

/// The 4-item bottom nav shared by Home, Capture, Sync Status, and Settings
/// (Screen 0's spec: "Home, Capture, Sync Status, Settings — no 5th item
/// needed at this stage"). Each of those screens embeds this in its
/// Scaffold's bottomNavigationBar.
class AppBottomNav extends StatelessWidget {
  final int currentIndex;

  const AppBottomNav({super.key, required this.currentIndex});

  static const _routes = ['/home', '/capture/new', '/sync-status', '/settings'];

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return BottomNavigationBar(
      currentIndex: currentIndex,
      onTap: (i) {
        if (i == currentIndex) return;
        context.go(_routes[i]);
      },
      backgroundColor: colors.card,
      selectedItemColor: colors.primary,
      unselectedItemColor: colors.mutedForeground,
      type: BottomNavigationBarType.fixed,
      items: const [
        BottomNavigationBarItem(icon: Icon(Icons.home_outlined), label: 'Home'),
        BottomNavigationBarItem(icon: Icon(Icons.add_box_outlined), label: 'Capture'),
        BottomNavigationBarItem(icon: Icon(Icons.sync_outlined), label: 'Sync'),
        BottomNavigationBarItem(icon: Icon(Icons.settings_outlined), label: 'Settings'),
      ],
    );
  }
}
