import 'dart:io';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:uuid/uuid.dart';

import '../../mock/mock_data.dart';
import '../../models/location_models.dart';
import '../../models/shipment_models.dart';
import '../../offline/offline_queue.dart';
import '../../theme/app_theme.dart';
import '../../theme/fresh_supplies_colors.dart';
import '../../widgets/app_bottom_nav.dart';
import '../../widgets/app_text_field.dart';
import '../../widgets/location_search_field.dart';
import '../../widgets/primary_button.dart';

/// Screen 4 — Shipment Capture Form. Route: /capture/new.
///
/// "Save" writes to the local offline queue immediately (no network call at
/// this point per Phase 4 scope), generates a client_id (UUID v4) at that
/// moment for later idempotent sync (Phase 5), and returns to Home with a
/// confirmation snackbar.
class ShipmentCaptureScreen extends StatefulWidget {
  const ShipmentCaptureScreen({super.key});

  @override
  State<ShipmentCaptureScreen> createState() => _ShipmentCaptureScreenState();
}

class _ShipmentCaptureScreenState extends State<ShipmentCaptureScreen> {
  String? _crop;
  final _quantityController = TextEditingController();
  final _notesController = TextEditingController();
  LocationSearchResult? _selectedLocation;
  XFile? _photo;
  bool _saving = false;

  @override
  void dispose() {
    _quantityController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _takePhoto(ImageSource source) async {
    final file = await ImagePicker().pickImage(source: source, maxWidth: 1600, imageQuality: 80);
    if (file != null) setState(() => _photo = file);
  }

  bool get _canSave =>
      _crop != null && (double.tryParse(_quantityController.text) ?? 0) > 0 && _selectedLocation != null;

  Future<void> _save() async {
    setState(() => _saving = true);
    const uuid = Uuid();
    final clientId = uuid.v4();
    final location = _selectedLocation!;
    // Writes to the local offline queue immediately — no network call on
    // this thread. OfflineQueue.add() fires a best-effort background sync
    // itself; this client_id is what makes a later retry idempotent
    // (POST /mobile/shipments/sync, per the mobile API contract).
    await OfflineQueue.instance.add(QueuedCapture(
      clientId: clientId,
      crop: _crop!,
      quantityKg: double.parse(_quantityController.text),
      capturedAt: DateTime.now(),
      lat: location.latitude,
      lon: location.longitude,
      notes: _notesController.text.trim().isEmpty ? null : _notesController.text.trim(),
    ));
    if (!mounted) return;
    setState(() => _saving = false);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Saved — will sync automatically.')),
    );
    context.go('/home');
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return Scaffold(
      appBar: AppBar(title: const Text('Log a shipment')),
      bottomNavigationBar: const AppBottomNav(currentIndex: 1),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          children: [
            Text('Crop', style: TextStyle(color: colors.mutedForeground, fontSize: 14, fontWeight: FontWeight.w500)),
            const SizedBox(height: AppSpacing.xs),
            _Dropdown<String>(
              value: _crop,
              hint: 'Select crop',
              items: kCropList.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
              onChanged: (v) => setState(() => _crop = v),
            ),
            const SizedBox(height: AppSpacing.lg),
            AppTextField(
              label: 'Quantity (kg)',
              hint: 'e.g. 250',
              controller: _quantityController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              onChanged: (_) => setState(() {}),
            ),
            const SizedBox(height: AppSpacing.lg),
            LocationSearchField(
              label: 'Location',
              selected: _selectedLocation,
              onSelected: (result) => setState(() => _selectedLocation = result),
              onClear: () => setState(() => _selectedLocation = null),
            ),
            const SizedBox(height: AppSpacing.lg),
            Text('Photo', style: TextStyle(color: colors.mutedForeground, fontSize: 14, fontWeight: FontWeight.w500)),
            const SizedBox(height: AppSpacing.xs),
            if (_photo != null)
              Stack(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(AppRadius.md),
                    child: Image.file(File(_photo!.path), height: 160, width: double.infinity, fit: BoxFit.cover),
                  ),
                  Positioned(
                    right: AppSpacing.sm,
                    top: AppSpacing.sm,
                    child: TextButton(
                      onPressed: () => _takePhoto(ImageSource.camera),
                      style: TextButton.styleFrom(backgroundColor: colors.card),
                      child: const Text('Retake'),
                    ),
                  ),
                ],
              )
            else
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _takePhoto(ImageSource.camera),
                      icon: const Icon(Icons.camera_alt_outlined),
                      label: const Text('Camera'),
                    ),
                  ),
                  const SizedBox(width: AppSpacing.md),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _takePhoto(ImageSource.gallery),
                      icon: const Icon(Icons.photo_library_outlined),
                      label: const Text('Gallery'),
                    ),
                  ),
                ],
              ),
            const SizedBox(height: AppSpacing.lg),
            AppTextField(label: 'Notes (optional)', hint: 'Anything worth flagging', controller: _notesController, maxLines: 3),
            const SizedBox(height: AppSpacing.xl),
            PrimaryButton(label: 'Save', loading: _saving, onPressed: _canSave ? _save : null),
            const SizedBox(height: AppSpacing.xl),
          ],
        ),
      ),
    );
  }
}

class _Dropdown<T> extends StatelessWidget {
  final T? value;
  final String hint;
  final List<DropdownMenuItem<T>> items;
  final ValueChanged<T?> onChanged;

  const _Dropdown({required this.value, required this.hint, required this.items, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final colors = context.colors;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
      decoration: BoxDecoration(
        color: colors.card,
        borderRadius: BorderRadius.circular(AppRadius.md),
        border: Border.all(color: colors.border),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<T>(
          value: value,
          hint: Text(hint, style: TextStyle(color: colors.mutedForeground)),
          isExpanded: true,
          items: items,
          onChanged: onChanged,
        ),
      ),
    );
  }
}
