import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../mock/mock_data.dart';
import '../../theme/fresh_supplies_colors.dart';

/// Screen 7 — Notifications. Route: /notifications.
/// Shared between farmer and driver (same screen, content differs by role).
/// Density: minimal.
class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final notifications = kMockNotifications;

    return Scaffold(
      appBar: AppBar(title: const Text('Notifications')),
      body: notifications.isEmpty
          ? Center(child: Text('No notifications yet.', style: TextStyle(color: colors.mutedForeground)))
          : ListView.separated(
              itemCount: notifications.length,
              separatorBuilder: (context, i) => Divider(height: 1, color: colors.border),
              itemBuilder: (context, i) {
                final n = notifications[i];
                return ListTile(
                  leading: Icon(
                    n.type == NotificationType.riskChange ? Icons.warning_amber_rounded : Icons.local_shipping_outlined,
                    color: n.type == NotificationType.riskChange ? colors.riskCritical : colors.primary,
                  ),
                  title: Text(n.title, style: TextStyle(color: colors.foreground)),
                  subtitle: Text(_relativeTime(n.timestamp), style: TextStyle(color: colors.mutedForeground, fontSize: 12)),
                  onTap: n.relatedShipmentId != null
                      ? () => context.push('/shipments/${n.relatedShipmentId}/recommendation')
                      : () => context.push('/driver/manifest'),
                );
              },
            ),
    );
  }

  String _relativeTime(DateTime t) {
    final diff = DateTime.now().difference(t);
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }
}
