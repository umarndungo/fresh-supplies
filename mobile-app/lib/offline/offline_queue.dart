import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../api/shipment_api.dart';
import '../models/shipment_models.dart';

/// Local-first capture queue (Screen 4 writes here immediately; Screen 5
/// reads/retries from here). Persisted to shared_preferences as JSON so
/// queued captures survive an app restart while still offline.
///
/// Idempotency: each QueuedCapture keeps the client_id it was created with
/// (Screen 4 generates it once, at save time) for the lifetime of the
/// queue entry — retrying a failed sync resubmits the SAME client_id, so a
/// partial failure (server created the shipment but the response was lost)
/// can't double-create it. This is the piece the build spec calls out as
/// "the one genuinely new client-side logic" in Phase 5.
class OfflineQueue extends ChangeNotifier {
  OfflineQueue._();
  static final OfflineQueue instance = OfflineQueue._();

  static const _storageKey = 'offline_capture_queue';

  final ShipmentApi _api = ShipmentApi();
  List<QueuedCapture> _items = [];
  bool _syncing = false;

  List<QueuedCapture> get items => List.unmodifiable(_items);
  bool get isSyncing => _syncing;

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_storageKey);
    if (raw == null) return;
    final decoded = jsonDecode(raw) as List;
    _items = decoded.map((e) => QueuedCapture.fromStorageJson(e as Map<String, dynamic>)).toList();
    notifyListeners();
  }

  Future<void> _persist() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_storageKey, jsonEncode(_items.map((i) => i.toStorageJson()).toList()));
  }

  Future<void> add(QueuedCapture capture) async {
    _items = [..._items, capture];
    notifyListeners();
    await _persist();
    // Best-effort immediate sync attempt; failures just leave it queued.
    unawaited(syncPending());
  }

  Future<void> retry(String clientId) async {
    _items = _items.map((i) => i.clientId == clientId ? i.copyWith(status: QueueStatus.pending, error: null) : i).toList();
    notifyListeners();
    await _persist();
    await syncPending();
  }

  /// Sends every PENDING or FAILED item — retrying a failed item is just
  /// "sync again with the same client_id," per the idempotency note above.
  Future<void> syncPending() async {
    final toSync = _items.where((i) => i.status != QueueStatus.synced).toList();
    if (toSync.isEmpty || _syncing) return;
    _syncing = true;
    notifyListeners();
    try {
      final results = await _api.sync(toSync);
      final byClientId = {for (final r in results) r.clientId: r};
      _items = _items.map((item) {
        final result = byClientId[item.clientId];
        if (result == null) return item;
        return result.status == 'failed'
            ? item.copyWith(status: QueueStatus.failed, error: result.error)
            : item.copyWith(status: QueueStatus.synced, serverId: result.serverId, riskTier: result.riskTier);
      }).toList();
      await _persist();
    } catch (_) {
      // Offline or server error — items stay pending for the next attempt
      // (manual retry, pull-to-refresh, or the next automatic attempt).
    } finally {
      _syncing = false;
      notifyListeners();
    }
  }
}
