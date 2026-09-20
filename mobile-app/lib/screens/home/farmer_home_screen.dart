import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../models/shipment_models.dart';
import '../../offline/offline_queue.dart';
import '../../theme/app_theme.dart';
import '../../theme/fresh_supplies_colors.dart';
import '../../widgets/app_bottom_nav.dart';
import '../../widgets/risk_tier_badge.dart';
import '../recommendation/recommendation_screen.dart';

/// Screen 0 — Farmer Home. Route: /home.
/// Orientation point after login — "what's happening with my shipments
/// right now," not a dashboard of everything. Density: minimal (farmer
/// tier). This is the root screen of the bottom-nav shell.
///
/// Known gap (Phase 5): the mobile API contract has no "list my shipments"
/// endpoint — only sync (write), sync-status (client_id -> server_id diffs),
/// and per-shipment recommendation. So this shows shipments captured *on
/// this device* (from the offline queue) once synced, not a farmer's full
/// history or a cooperative's shared pool. A real "my shipments" list needs
/// a new backend endpoint — out of scope for wiring against what exists.
class FarmerHomeScreen extends StatefulWidget {
  const FarmerHomeScreen({super.key});

  @override
  State<FarmerHomeScreen> createState() => _FarmerHomeScreenState();
}

class _FarmerHomeScreenState extends State<FarmerHomeScreen> {
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
    final synced = OfflineQueue.instance.items.where((i) => i.status == QueueStatus.synced && i.riskTier != null).toList()
      ..sort((a, b) => b.capturedAt.compareTo(a.capturedAt));
    final atRiskCount = synced.where((s) => riskTierFromApi(s.riskTier!) != RiskTier.fresh).length;
    final recent = synced.take(5).toList();

    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: Text('Fresh Supplies', style: TextStyle(color: colors.primary, fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () => context.push('/notifications'),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/capture/new'),
        backgroundColor: colors.primary,
        foregroundColor: colors.primaryForeground,
        child: const Icon(Icons.add),
      ),
      bottomNavigationBar: const AppBottomNav(currentIndex: 0),
      body: synced.isEmpty
          ? Center(
              child: Text(
                'No shipments yet — tap + to log your first harvest.',
                textAlign: TextAlign.center,
                style: TextStyle(color: colors.mutedForeground, fontSize: 15),
              ),
            )
          : ListView(
              padding: const EdgeInsets.all(AppSpacing.lg),
              children: [
                _HeroCard(atRiskCount: atRiskCount),
                const SizedBox(height: AppSpacing.xl),
                Text('Recent shipments', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: colors.foreground)),
                const SizedBox(height: AppSpacing.sm),
                ...recent.map((s) => _ShipmentRow(capture: s)),
              ],
            ),
    );
  }
}

class _HeroCard extends StatelessWidget {
  final int atRiskCount;

  const _HeroCard({required this.atRiskCount});

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final allClear = atRiskCount == 0;
    final tint = allClear ? colors.riskFresh : colors.riskCritical;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppSpacing.xl),
      decoration: BoxDecoration(
        color: tint.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(AppRadius.xl),
        border: Border.all(color: tint.withValues(alpha: 0.4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            allClear ? 'All clear today' : '$atRiskCount shipment${atRiskCount == 1 ? '' : 's'} need attention',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: tint),
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(
            allClear ? 'No shipments are at risk right now.' : 'At-risk or critical shipments right now.',
            style: TextStyle(color: colors.foreground.withValues(alpha: 0.8), fontSize: 14),
          ),
        ],
      ),
    );
  }
}

class _ShipmentRow extends StatelessWidget {
  final QueuedCapture capture;

  const _ShipmentRow({required this.capture});

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final tier = riskTierFromApi(capture.riskTier!) ?? RiskTier.fresh;
    return InkWell(
      onTap: () => context.push(
        '/shipments/${capture.serverId}/recommendation',
        extra: RecommendationArgs(crop: capture.crop, quantityKg: capture.quantityKg, lat: capture.lat, lon: capture.lon),
      ),
      borderRadius: BorderRadius.circular(AppRadius.lg),
      child: Container(
        margin: const EdgeInsets.only(bottom: AppSpacing.sm),
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: colors.card,
          borderRadius: BorderRadius.circular(AppRadius.lg),
          border: Border.all(color: colors.border),
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(capture.crop, style: TextStyle(fontWeight: FontWeight.w600, color: colors.foreground)),
                  Text('${capture.quantityKg.toStringAsFixed(0)} kg', style: TextStyle(color: colors.mutedForeground, fontSize: 13)),
                ],
              ),
            ),
            RiskTierBadge(tier: tier),
          ],
        ),
      ),
    );
  }
}
