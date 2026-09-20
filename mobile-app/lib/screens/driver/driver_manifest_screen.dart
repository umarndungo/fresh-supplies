import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../api/driver_api.dart';
import '../../models/driver_models.dart';
import '../../theme/app_theme.dart';
import '../../theme/fresh_supplies_colors.dart';
import '../../widgets/async_state_view.dart';
import '../../widgets/risk_tier_badge.dart';
import '../../widgets/stop_tile.dart';

enum _ManifestView { list, calendar }

/// Screen 8 — Driver Manifest. Route: /driver/manifest.
/// Driver density (denser than farmer screens) — this screen legitimately
/// benefits from showing more at once. Cooperative pickups are already
/// grouped server-side into one stop per collection point; renders exactly
/// what the manifest endpoint returns, no client-side re-fragmentation.
class DriverManifestScreen extends StatefulWidget {
  const DriverManifestScreen({super.key});

  @override
  State<DriverManifestScreen> createState() => _DriverManifestScreenState();
}

class _DriverManifestScreenState extends State<DriverManifestScreen> {
  final _api = DriverApi();
  DateTime _date = DateTime.now();
  _ManifestView _view = _ManifestView.list;
  ViewState _state = ViewState.loading;
  List<ManifestStop> _stops = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _state = ViewState.loading);
    try {
      final stops = await _api.getManifest(_date);
      if (!mounted) return;
      setState(() {
        _stops = stops;
        _state = stops.isEmpty ? ViewState.empty : ViewState.content;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _state = ViewState.error);
    }
  }

  void _changeDate(int deltaDays) {
    setState(() => _date = _date.add(Duration(days: deltaDays)));
    _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(icon: const Icon(Icons.chevron_left), onPressed: () => _changeDate(-1)),
            Text(_formatDate(_date)),
            IconButton(icon: const Icon(Icons.chevron_right), onPressed: () => _changeDate(1)),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(_view == _ManifestView.list ? Icons.calendar_month_outlined : Icons.view_list_outlined),
            tooltip: _view == _ManifestView.list ? 'Calendar view' : 'List view',
            onPressed: () => setState(() => _view = _view == _ManifestView.list ? _ManifestView.calendar : _ManifestView.list),
          ),
        ],
      ),
      body: AsyncStateView(
        state: _state,
        emptyMessage: 'No stops scheduled for this day.',
        errorMessage: "Couldn't load manifest — check your connection",
        onRetry: _load,
        content: _view == _ManifestView.list
            ? ListView.builder(
                padding: const EdgeInsets.all(AppSpacing.md),
                itemCount: _stops.length,
                itemBuilder: (context, i) {
                  final stop = _stops[i];
                  return StopTile(
                    sequence: stop.sequence,
                    collectionPointName: stop.cooperativeName ?? stop.pickupLabel,
                    crop: stop.crop,
                    quantityKg: stop.quantityKg,
                    riskTier: riskTierFromApi(stop.riskTier),
                    onTap: () => context.push('/driver/stops/${stop.shipmentId}', extra: stop),
                  );
                },
              )
            : _CalendarPlaceholder(stopCount: _stops.length),
      ),
    );
  }

  String _formatDate(DateTime d) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return '${d.day} ${months[d.month - 1]} ${d.year}';
  }
}

class _CalendarPlaceholder extends StatelessWidget {
  final int stopCount;

  const _CalendarPlaceholder({required this.stopCount});

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.calendar_month_outlined, size: 48, color: colors.mutedForeground),
          const SizedBox(height: AppSpacing.md),
          Text('$stopCount stop${stopCount == 1 ? '' : 's'} on this day', style: TextStyle(color: colors.foreground)),
        ],
      ),
    );
  }
}
