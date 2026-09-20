import 'package:flutter/material.dart';

import '../../models/shipment_models.dart';
import '../../offline/offline_queue.dart';
import '../../theme/app_theme.dart';
import '../../theme/fresh_supplies_colors.dart';
import '../../widgets/app_bottom_nav.dart';

/// Screen 5 — Sync/Offline Queue Status. Route: /sync-status.
/// List-based rather than card-based — closer to a status log than a
/// decision screen. Pull-to-refresh triggers a manual sync attempt; the
/// queue also syncs automatically in the background (OfflineQueue.add()).
class SyncStatusScreen extends StatefulWidget {
  const SyncStatusScreen({super.key});

  @override
  State<SyncStatusScreen> createState() => _SyncStatusScreenState();
}

class _SyncStatusScreenState extends State<SyncStatusScreen> {
  @override
  void initState() {
    super.initState();
    OfflineQueue.instance.addListener(_onQueueChanged);
  }

  @override
  void dispose() {
    OfflineQueue.instance.removeListener(_onQueueChanged);
    super.dispose();
  }

  void _onQueueChanged() => setState(() {});

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final queue = OfflineQueue.instance.items;

    return Scaffold(
      appBar: AppBar(title: const Text('Sync status')),
      bottomNavigationBar: const AppBottomNav(currentIndex: 2),
      body: queue.isEmpty
          ? Center(
              child: Text("Nothing queued — you're all synced.", style: TextStyle(color: colors.mutedForeground, fontSize: 15)),
            )
          : RefreshIndicator(
              onRefresh: OfflineQueue.instance.syncPending,
              child: ListView.separated(
                padding: const EdgeInsets.all(AppSpacing.md),
                itemCount: queue.length,
                separatorBuilder: (context, i) => const SizedBox(height: AppSpacing.sm),
                itemBuilder: (context, i) => _QueueRow(
                  item: queue[i],
                  onRetry: () => OfflineQueue.instance.retry(queue[i].clientId),
                ),
              ),
            ),
    );
  }
}

class _QueueRow extends StatelessWidget {
  final QueuedCapture item;
  final VoidCallback onRetry;

  const _QueueRow({required this.item, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final (chipColor, chipFg, label) = switch (item.status) {
      QueueStatus.pending => (colors.muted, colors.mutedForeground, 'Pending'),
      QueueStatus.synced => (colors.primary, colors.primaryForeground, 'Synced'),
      QueueStatus.failed => (colors.destructive, colors.destructiveForeground, 'Failed'),
    };
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: colors.card,
        borderRadius: BorderRadius.circular(AppRadius.md),
        border: Border.all(color: colors.border),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('${item.crop} · ${item.quantityKg.toStringAsFixed(0)} kg', style: TextStyle(color: colors.foreground, fontWeight: FontWeight.w500)),
                if (item.status == QueueStatus.failed && item.error != null)
                  Text(item.error!, style: TextStyle(color: colors.destructive, fontSize: 12)),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.sm, vertical: 2),
            decoration: BoxDecoration(color: chipColor, borderRadius: BorderRadius.circular(AppRadius.pill)),
            child: Text(label, style: TextStyle(color: chipFg, fontSize: 12, fontWeight: FontWeight.w600)),
          ),
          if (item.status == QueueStatus.failed) ...[
            const SizedBox(width: AppSpacing.sm),
            TextButton(onPressed: onRetry, child: const Text('Retry')),
          ],
        ],
      ),
    );
  }
}
