import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../api/driver_api.dart';
import '../../models/driver_models.dart';
import '../../theme/app_theme.dart';
import '../../theme/fresh_supplies_colors.dart';
import '../../widgets/primary_button.dart';
import '../../widgets/risk_tier_badge.dart';

/// Screen 9 — Stop Detail / Confirm Pickup. Route: /driver/stops/:id.
/// Density here means the manifest list (Screen 8), not this detail view —
/// this individual screen is simple by nature. "Confirm pickup" is
/// idempotent: safe to tap twice, shows a disabled/checked state after the
/// first success rather than allowing repeated taps to do anything.
///
/// `stop` comes from the manifest row that was tapped (there's no "get
/// stop by id" mobile endpoint — only the manifest list) — a direct deep
/// link without it shows "stop not found" rather than guessing.
class StopDetailScreen extends StatefulWidget {
  final String stopId;
  final ManifestStop? stop;

  const StopDetailScreen({super.key, required this.stopId, this.stop});

  @override
  State<StopDetailScreen> createState() => _StopDetailScreenState();
}

class _StopDetailScreenState extends State<StopDetailScreen> {
  final _api = DriverApi();
  bool _confirming = false;
  bool _confirmed = false;
  String? _error;

  Future<void> _confirmPickup() async {
    if (_confirming || _confirmed) return; // idempotent — a second tap is a no-op
    final stop = widget.stop!;
    setState(() {
      _confirming = true;
      _error = null;
    });
    try {
      await _api.confirmStop(stop.shipmentId, lat: stop.lat, lon: stop.lon);
      if (!mounted) return;
      setState(() {
        _confirming = false;
        _confirmed = true;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _confirming = false;
        _error = "Couldn't confirm — check your connection and try again.";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final stop = widget.stop;
    if (stop == null) {
      return Scaffold(
        appBar: AppBar(),
        body: Center(child: Text('Stop not found.', style: TextStyle(color: colors.mutedForeground))),
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text('Stop ${stop.sequence}')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(stop.cooperativeName ?? stop.pickupLabel, style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: colors.foreground)),
              const SizedBox(height: AppSpacing.xs),
              Text(stop.pickupLabel, style: TextStyle(color: colors.mutedForeground, fontSize: 14)),
              const SizedBox(height: AppSpacing.md),
              Row(
                children: [
                  Text('${stop.crop} · ${stop.quantityKg.toStringAsFixed(0)} kg', style: TextStyle(color: colors.foreground, fontWeight: FontWeight.w500)),
                  const SizedBox(width: AppSpacing.sm),
                  RiskTierBadge(tier: riskTierFromApi(stop.riskTier) ?? RiskTier.fresh, small: true),
                ],
              ),
              const SizedBox(height: AppSpacing.lg),
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(AppRadius.lg),
                  child: FlutterMap(
                    options: MapOptions(
                      initialCenter: LatLng(stop.lat, stop.lon),
                      initialZoom: 13,
                      interactionOptions: const InteractionOptions(flags: InteractiveFlag.none),
                    ),
                    children: [
                      TileLayer(
                        urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                        userAgentPackageName: 'com.freshsupplies.mobile_app',
                      ),
                      MarkerLayer(markers: [
                        Marker(point: LatLng(stop.lat, stop.lon), width: 40, height: 40, child: Icon(Icons.location_pin, color: colors.destructive, size: 40)),
                      ]),
                    ],
                  ),
                ),
              ),
              if (_error != null) ...[
                const SizedBox(height: AppSpacing.sm),
                Text(_error!, style: TextStyle(color: colors.destructive, fontSize: 13)),
              ],
              const SizedBox(height: AppSpacing.lg),
              PrimaryButton(
                label: _confirmed ? 'Pickup confirmed ✓' : 'Confirm pickup',
                loading: _confirming,
                onPressed: _confirmed ? null : _confirmPickup,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
