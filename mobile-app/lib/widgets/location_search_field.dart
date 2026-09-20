import 'dart:async';

import 'package:flutter/material.dart';

import '../api/location_api.dart';
import '../models/location_models.dart';
import '../theme/app_theme.dart';
import '../theme/fresh_supplies_colors.dart';
import 'app_text_field.dart';

/// Mobile equivalent of the web app's LocationPicker
/// (src/components/map/location-picker.tsx) — search-as-you-type against
/// the same GET /locations/search endpoint, replacing the old tap-on-map
/// picker for shipment capture.
class LocationSearchField extends StatefulWidget {
  final String label;
  final LocationSearchResult? selected;
  final ValueChanged<LocationSearchResult> onSelected;
  final VoidCallback onClear;

  const LocationSearchField({
    super.key,
    required this.label,
    required this.selected,
    required this.onSelected,
    required this.onClear,
  });

  @override
  State<LocationSearchField> createState() => _LocationSearchFieldState();
}

class _LocationSearchFieldState extends State<LocationSearchField> {
  final _controller = TextEditingController();
  final _api = LocationApi();
  Timer? _debounce;
  List<LocationSearchResult> _results = [];
  bool _searching = false;
  bool _error = false;
  bool _dismissed = false;

  @override
  void dispose() {
    _debounce?.cancel();
    _controller.dispose();
    super.dispose();
  }

  void _onChanged(String value) {
    _dismissed = false;
    _debounce?.cancel();
    final query = value.trim();
    if (query.length < 2) {
      setState(() {
        _results = [];
        _error = false;
        _searching = false;
      });
      return;
    }
    setState(() => _searching = true);
    _debounce = Timer(const Duration(milliseconds: 400), () async {
      try {
        final results = await _api.search(query);
        if (!mounted) return;
        setState(() {
          _results = results;
          _searching = false;
          _error = false;
        });
      } catch (_) {
        if (!mounted) return;
        setState(() {
          _results = [];
          _searching = false;
          _error = true;
        });
      }
    });
  }

  void _select(LocationSearchResult result) {
    widget.onSelected(result);
    setState(() {
      _controller.text = result.displayName;
      _dismissed = true;
    });
    FocusScope.of(context).unfocus();
  }

  void _clear() {
    widget.onClear();
    setState(() {
      _controller.clear();
      _results = [];
      _dismissed = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    final showResults = !_dismissed && _controller.text.trim().length >= 2;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(widget.label, style: TextStyle(color: colors.mutedForeground, fontSize: 14, fontWeight: FontWeight.w500)),
        const SizedBox(height: AppSpacing.xs),
        if (widget.selected != null) ...[
          Container(
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.sm),
            decoration: BoxDecoration(color: colors.muted, borderRadius: BorderRadius.circular(AppRadius.md)),
            child: Row(
              children: [
                Icon(Icons.location_on_outlined, size: 18, color: colors.mutedForeground),
                const SizedBox(width: AppSpacing.sm),
                Expanded(
                  child: Text(
                    widget.selected!.displayName,
                    style: TextStyle(color: colors.foreground, fontSize: 14),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.close, size: 18, color: colors.mutedForeground),
                  onPressed: _clear,
                  visualDensity: VisualDensity.compact,
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
        ],
        AppTextField(
          hint: 'Search for a town or collection point',
          controller: _controller,
          onChanged: _onChanged,
          prefix: Padding(
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
            child: Icon(Icons.search, size: 20, color: colors.mutedForeground),
          ),
        ),
        if (showResults) ...[
          const SizedBox(height: AppSpacing.xs),
          if (_searching)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
              child: Text('Searching Kenyan locations…', style: TextStyle(color: colors.mutedForeground, fontSize: 13)),
            )
          else if (_error)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
              child: Text('Location search is unavailable. Try again.', style: TextStyle(color: colors.destructive, fontSize: 13)),
            )
          else if (_results.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
              child: Text('No Kenyan locations found.', style: TextStyle(color: colors.mutedForeground, fontSize: 13)),
            )
          else
            Container(
              constraints: const BoxConstraints(maxHeight: 220),
              decoration: BoxDecoration(
                border: Border.all(color: colors.border),
                borderRadius: BorderRadius.circular(AppRadius.md),
              ),
              child: ListView.separated(
                shrinkWrap: true,
                padding: EdgeInsets.zero,
                itemCount: _results.length,
                separatorBuilder: (_, _) => Divider(height: 1, color: colors.border),
                itemBuilder: (context, index) {
                  final result = _results[index];
                  return ListTile(
                    dense: true,
                    title: Text(result.displayName, style: TextStyle(fontSize: 14, color: colors.foreground)),
                    subtitle: result.county != null
                        ? Text(result.county!, style: TextStyle(fontSize: 12, color: colors.mutedForeground))
                        : null,
                    onTap: () => _select(result),
                  );
                },
              ),
            ),
        ],
      ],
    );
  }
}
