import 'package:flutter/material.dart';

import '../../api/shipment_api.dart';
import '../../models/shipment_models.dart';
import '../../theme/app_theme.dart';
import '../../theme/fresh_supplies_colors.dart';
import '../../widgets/async_state_view.dart';
import '../../widgets/risk_tier_badge.dart';

/// The facts GET /mobile/shipments/{id}/recommendation needs as query
/// params — Home passes these along from the QueuedCapture it already has;
/// there's no "fetch shipment by id" mobile endpoint to re-derive them from
/// just an id (see farmer_home_screen.dart's Phase 5 gap note).
class RecommendationArgs {
  final String crop;
  final double quantityKg;
  final double lat;
  final double lon;

  const RecommendationArgs({required this.crop, required this.quantityKg, required this.lat, required this.lon});
}

/// Screen 6 — Recommendation View. Route: /shipments/:id/recommendation.
/// The single largest visual element is the risk badge; resist adding a
/// chart or secondary stats here — this screen's whole purpose is restraint.
/// This is the screen most likely to be used with poor connectivity, so the
/// error state needs to be genuinely helpful, not just an icon.
class RecommendationScreen extends StatefulWidget {
  final String shipmentId;
  final RecommendationArgs? args;

  const RecommendationScreen({super.key, required this.shipmentId, this.args});

  @override
  State<RecommendationScreen> createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends State<RecommendationScreen> {
  final _api = ShipmentApi();
  ViewState _state = ViewState.loading;
  RecommendationResult? _result;
  bool _showAlternates = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final args = widget.args;
    if (args == null) {
      setState(() => _state = ViewState.error);
      return;
    }
    setState(() => _state = ViewState.loading);
    try {
      final result = await _api.getRecommendation(
        shipmentId: widget.shipmentId,
        crop: args.crop,
        quantityKg: args.quantityKg,
        lat: args.lat,
        lon: args.lon,
      );
      if (!mounted) return;
      setState(() {
        _result = result;
        _state = ViewState.content;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _state = ViewState.error);
    }
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final result = _result;
    return Scaffold(
      appBar: AppBar(title: Text(widget.args != null ? '${widget.args!.crop} · ${widget.args!.quantityKg.toStringAsFixed(0)} kg' : 'Recommendation')),
      body: AsyncStateView(
        state: _state,
        errorMessage: "Couldn't load recommendation — check your connection",
        onRetry: _load,
        content: result == null
            ? const SizedBox.shrink()
            : Padding(
                padding: const EdgeInsets.all(AppSpacing.xl),
                child: Column(
                  children: [
                    const SizedBox(height: AppSpacing.lg),
                    Center(child: RiskTierBadge(tier: riskTierFromApi(result.riskTier) ?? RiskTier.fresh)),
                    const SizedBox(height: AppSpacing.lg),
                    Text(
                      result.riskLabel,
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 17, color: colors.foreground, fontWeight: FontWeight.w500),
                    ),
                    const SizedBox(height: AppSpacing.xl),
                    if (result.recommendedMarket != null) _MarketCard(market: result.recommendedMarket!, primary: true),
                    if (result.alternateMarkets.isNotEmpty) ...[
                      const SizedBox(height: AppSpacing.md),
                      TextButton(
                        onPressed: () => setState(() => _showAlternates = !_showAlternates),
                        child: Text(_showAlternates ? 'Hide other options' : 'See other options'),
                      ),
                      if (_showAlternates)
                        ...result.alternateMarkets.map(
                          (m) => Padding(
                            padding: const EdgeInsets.only(top: AppSpacing.sm),
                            child: _MarketCard(market: m, primary: false),
                          ),
                        ),
                    ],
                  ],
                ),
              ),
      ),
    );
  }
}

class _MarketCard extends StatelessWidget {
  final Map<String, dynamic> market;
  final bool primary;

  const _MarketCard({required this.market, required this.primary});

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final name = market['name'] as String? ?? 'Market';
    final distanceKm = (market['distance_km'] as num?)?.toDouble() ?? 0;
    final pricePerKg = (market['est_price_per_kg'] as num?)?.toDouble() ?? 0;
    final revenue = (market['est_revenue_retained'] as num?)?.toDouble() ?? 0;
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(primary ? AppSpacing.lg : AppSpacing.md),
      decoration: BoxDecoration(
        color: colors.card,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: primary ? colors.primary : colors.border, width: primary ? 2 : 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(name, style: TextStyle(fontWeight: FontWeight.w700, fontSize: primary ? 17 : 14, color: colors.foreground)),
          const SizedBox(height: AppSpacing.xs),
          Text(
            '${distanceKm.toStringAsFixed(0)} km · ${pricePerKg.toStringAsFixed(0)} KES/kg',
            style: TextStyle(color: colors.mutedForeground, fontSize: primary ? 14 : 12),
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(
            '~${revenue.toStringAsFixed(0)} KES estimated revenue',
            style: TextStyle(color: colors.primary, fontWeight: FontWeight.w600, fontSize: primary ? 15 : 13),
          ),
        ],
      ),
    );
  }
}
