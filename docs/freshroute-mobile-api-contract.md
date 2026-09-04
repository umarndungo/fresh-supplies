# FreshRoute AI — Mobile API Contract (Draft v0.2)

Scope: endpoints needed for a field-capture / logistics mobile app on top of the
existing FastAPI backend. This extends (does not replace) the current `/auth`,
`/produce`, `/shipments`, `/ml` routes. New routes are namespaced under `/mobile/*`
where the mobile client's needs diverge from the web contract (offline sync, phone
auth, simplified payloads).

**v0.2 changelog:** resolved the three open questions from v0.1 — dual ownership
model (cooperative or individual, user-selected), local-disk photo storage (Oracle
Free Tier target), and a staging-table sync architecture. See §2.1, §3.2, and §3.3.

---

## 1. Design principles

- **Offline-first**: every write the app makes must be queueable locally and safe to
  replay. No endpoint should assume the client was online when the user acted.
- **Idempotent writes**: every mutating mobile request carries a client-generated
  `client_id` (UUID) so retried/duplicate syncs don't create duplicate records.
- **Payload minimalism**: mobile responses should be pre-shaped for the UI (risk tier
  + one recommended market), not the full `/ml` response — save bytes and battery on
  poor rural connections.
- **Reuse the existing JWT + role system** — don't fork auth logic, just add a phone/OTP
  *login method* that issues the same token shape as the web app.

---

## 2. Auth — phone + OTP

Farmers and drivers should not need email/password. Add an OTP path alongside the
existing email/password login; both should terminate in the same JWT contract so the
rest of the API doesn't need to know which method was used.

### `POST /mobile/auth/otp/request`
```json
// Request
{ "phone_number": "+254712345678" }

// Response 200
{ "status": "sent", "expires_in_seconds": 300 }
```
- Rate-limit aggressively (e.g. 3 requests / 10 min / number) — this is the obvious
  abuse vector on an open endpoint.
- Deliver via SMS provider (Africa's Talking / Twilio) — out of scope for this contract,
  but flag it as a real infra dependency, not an afterthought.

### `POST /mobile/auth/otp/verify`
```json
// Request
{ "phone_number": "+254712345678", "code": "482913" }

// Response 200 — same shape as existing /auth/login
{
  "data": {
    "accessToken": "...",
    "expiresIn": 900,
    "user": {
      "id": "uuid",
      "phone_number": "+254712345678",
      "role": "FARMER_COOPERATIVE",
      "full_name": null            // null until profile completed
    }
  }
}
```
- Refresh token still goes in an httpOnly cookie for web, but mobile has no cookie jar
  by default — issue the refresh token in the response body for mobile clients instead,
  and store it in device secure storage (Keychain / EncryptedSharedPreferences), never
  plain AsyncStorage/localStorage-equivalent.
- First-time verify with no existing user → auto-create account with the phone number
  and a `PENDING_PROFILE` flag; prompt for account type + name/role on first app open
  (see §2.1).

### `POST /mobile/auth/refresh`
Same semantics as the web refresh endpoint, but reads the refresh token from the
request body (not a cookie).

## 2.1 Account model — cooperative vs. individual

**Decision:** both models are supported. On first profile completion, the user picks
an `account_type`, and everything downstream (produce/shipment ownership, manifest
queries, notifications) branches on it rather than assuming one shape.

```json
// account_type: "COOPERATIVE" | "INDIVIDUAL"
```

- **`INDIVIDUAL`** — a single farmer or a standalone venture. Shipments and produce
  are owned directly by `user_id`. No grouping entity involved.
- **`COOPERATIVE`** — a multi-farmer cooperative. Shipments and produce are owned by
  a `cooperative_id`, with the acting `user_id` recorded separately as the
  *submitter* (so a manifest or history view can show "who logged this" without
  changing who the record belongs to).

### `POST /mobile/auth/complete-profile`
```json
// Request
{
  "full_name": "Adeline Joe",
  "account_type": "COOPERATIVE",           // or "INDIVIDUAL"
  "cooperative_name": "Kiambu Growers Coop", // required only if COOPERATIVE
  "cooperative_id": null                    // set instead of cooperative_name if
                                             // joining an existing cooperative —
                                             // see join-flow note below
}

// Response 200
{
  "data": {
    "user": {
      "id": "uuid",
      "account_type": "COOPERATIVE",
      "cooperative_id": "uuid",
      "role": "FARMER_COOPERATIVE"
    }
  }
}
```
- If `cooperative_name` is given with no existing `cooperative_id`, this creates a
  new cooperative and makes the user its first admin member. Joining an *existing*
  cooperative (invite code, admin approval, etc.) is a real product flow but is
  explicitly **out of scope for this contract version** — flag it as a follow-up
  spec once the invite/approval UX is decided, don't half-build it here.
- `INDIVIDUAL` accounts get `cooperative_id: null` everywhere — every downstream
  schema in this doc treats `cooperative_id` as nullable, not as a required field.

### Schema impact on `/mobile/shipments/sync` (§3) and produce records
Every shipment/produce row now carries both:
```json
{
  "owner_type": "COOPERATIVE",      // or "INDIVIDUAL", copied from the submitting user
  "cooperative_id": "uuid",         // null when owner_type is INDIVIDUAL
  "submitted_by_user_id": "uuid"    // always set — who physically captured it
}
```
This means a cooperative admin's view of "our shipments" is a `cooperative_id` filter,
while an individual's view is a `submitted_by_user_id` filter — same underlying query
shape, different key, so this doesn't need two separate code paths on the backend,
just a conditional filter column.

### Schema impact on `/mobile/driver/manifest` (§5)
The manifest query needs to resolve stops across **all shipments belonging to a
cooperative**, not just ones a single user submitted — a driver picking up from a
cooperative's collection point is picking up produce from many farmers under one
`cooperative_id`. Individual-venture pickups stay scoped to one `submitted_by_user_id`.
See the updated query note in §5.

---

## 3. Offline shipment capture + sync

This is the core mobile-specific surface. The client writes to a local queue always;
sync is a background reconciliation, not a blocking user action.

## 3.1 Server-side persistence model — staging table

**Decision:** `/mobile/shipments/sync` writes to a new `shipment_sync_staging` table,
not directly to `shipments`. A separate reconciliation step promotes staged rows into
`shipments` (and runs `/ml/predict-spoilage` as part of that promotion, or inline at
staging time — see below).

Why: the web CRUD contract for `/shipments` assumes one clean row per request, created
by an already-authenticated, already-online user. The mobile sync contract has
different semantics entirely — batched, idempotent-by-`client_id`, partial-failure-
tolerant, and possibly arriving hours after capture. Overloading `shipments` with both
write patterns means every future change to one risks breaking the other. A staging
table keeps them decoupled:

```
shipment_sync_staging
├── client_id (unique, the idempotency key)
├── raw payload (crop, quantity, captured_at, location, notes, owner_type,
│   cooperative_id, submitted_by_user_id — see §2.1)
├── sync_received_at
├── reconciliation_status: PENDING | RECONCILED | FAILED
└── reconciled_shipment_id (nullable, set once promoted)
```

- The risk tier returned inline in the sync response (see below) is computed against
  the *staged* row immediately, so the UI doesn't wait on reconciliation to show a
  badge — reconciliation is about getting the record into the canonical `shipments`
  table cleanly, not about gating the user-facing prediction.
- Reconciliation can run as a lightweight periodic job (e.g. every few minutes) rather
  than synchronously in the request — keeps the sync endpoint fast and simple, and
  gives a natural place to handle edge cases (malformed payloads, unknown crop names)
  without failing the whole batch back to the client.
- `reconciliation_status: FAILED` rows should be visible somewhere in the web
  dashboard (an "sync issues" list for admins) rather than silently dropped — worth a
  small follow-up ticket once the mobile app is live.

### `POST /mobile/shipments/sync`
Batched upsert — the client sends everything queued since last successful sync in one
call, rather than one request per shipment (critical for spotty connectivity: fewer
round trips, fewer partial-failure states to reason about).

```json
// Request
{
  "shipments": [
    {
      "client_id": "b3f1c2a0-...",      // UUID generated on-device at capture time
      "crop": "Tomatoes",
      "quantity_kg": 340,
      "captured_at": "2026-09-01T06:12:00Z",   // device local time, ISO 8601
      "location": { "lat": -1.2921, "lon": 36.8219 },
      "photo_ref": "local://shipment_photos/b3f1c2a0.jpg",  // uploaded separately, see below
      "notes": "Harvested this morning, slight bruising on ~5%"
    }
  ]
}

// Response 200
{
  "results": [
    {
      "client_id": "b3f1c2a0-...",
      "status": "created",             // created | duplicate | error
      "server_id": "uuid",
      "risk_tier": "AT_RISK",          // pre-computed, see §4
      "error": null
    }
  ]
}
```

- **`client_id` is the idempotency key.** If the same `client_id` arrives twice (e.g.
  the app retried after a timeout but the first request actually succeeded), the
  server returns `"status": "duplicate"` with the original `server_id` — never creates
  a second row.
- Partial failure is expected and normal: one shipment in the batch can `error` while
  the others `created` — the client must handle a mixed-result array, not treat the
  whole batch as atomic.
- The server runs `/ml/predict-spoilage` on each created shipment synchronously and
  returns the risk tier inline, so the app can show a badge immediately without a
  second round trip.

## 3.2 Photo storage — local disk (Oracle Free Tier target)

**Decision:** start with local disk under the backend's filesystem, matching the
existing artifact-storage approach used for ML model files — no S3-compatible object
store dependency yet. Hosting target is Oracle Cloud Free Tier to start.

Implications worth designing around now, since they're cheap to handle early and
expensive to retrofit:
- **Disk quota is finite on a free-tier instance.** Store a compressed/resized
  version on upload (e.g. max 1600px long edge, JPEG quality ~80) rather than the raw
  camera file — a resize step on the backend, not a client-side promise, since you
  can't guarantee every device does this consistently.
- **No built-in redundancy.** Local disk on a single free-tier VM is a single point
  of failure for photos. This is an acceptable starting tradeoff, but it should be a
  named, tracked limitation (add to the project's known-limitations doc) rather than
  an assumption nobody revisits — plan a migration path to object storage
  (Oracle's own bucket service or S3-compatible) once volume or reliability
  requirements grow past what a single-VM disk can reasonably guarantee.
- **File path, not blob, gets stored in the DB.** `shipment_sync_staging` /
  `shipments` should store a relative path or reference key, not raw bytes — keeps
  the door open to swapping the storage backend later without a schema change, only
  a storage-adapter change.
- **Serve photos through the backend, not by exposing the disk path directly** — an
  authenticated `GET /shipments/{id}/photo` style route, so photo access still
  respects the same auth/RBAC rules as everything else, rather than being a static
  file path anyone with the URL can hit.

### `POST /mobile/shipments/photo-upload`
Separate multipart endpoint for photos, referenced by `client_id`. Decoupled from the
sync call so a large photo upload failure doesn't block the shipment record itself
from syncing — the shipment exists with `photo_status: "pending"` until the photo
lands.

```
Content-Type: multipart/form-data
fields: client_id, file
```

### `GET /mobile/shipments/sync-status?since=<ISO8601>`
Pull-side of sync: what has the server-side changed since the client's last known
state (e.g. a logistics manager reassigned a shipment's destination from the web app).
Returns a delta, not a full re-fetch.

---

## 4. Simplified risk + market view

The web app can show raw probabilities and a ranked table; the mobile app should not.
Field users need one number and one action.

### `GET /mobile/shipments/{id}/recommendation`
```json
// Response 200
{
  "risk_tier": "AT_RISK",             // FRESH | AT_RISK | CRITICAL
  "risk_label": "Sell within 24 hours",   // pre-written copy per tier, not raw prob
  "recommended_market": {
    "name": "Nairobi Gikomba",
    "distance_km": 42,
    "est_price_per_kg": 38,
    "est_revenue_retained": 11492
  },
  "alternate_markets": [ /* top 2 more, same shape, for a "see other options" tap */ ]
}
```
- Deliberately **not** the full `/ml/recommend-market` payload — that returns all 10
  markets ranked with raw floats, which is analyst-facing, not farmer-facing.
- `risk_label` should be a small server-side lookup table (tier → action sentence),
  translated per locale (see §6), not generated ad hoc per request — keeps the copy
  consistent and easy to translate/audit.

---

## 5. Driver / logistics role

Separate from the farmer capture flow — a driver's app screen is a manifest + route,
not a data-entry form.

### `GET /mobile/driver/manifest?date=2026-09-02`
```json
{
  "stops": [
    {
      "shipment_id": "uuid",
      "owner_type": "COOPERATIVE",          // or "INDIVIDUAL", see §2.1
      "cooperative_name": "Kiambu Growers Coop",  // null for INDIVIDUAL stops
      "crop": "Tomatoes",
      "quantity_kg": 340,
      "pickup_location": { "lat": -1.29, "lon": 36.82, "label": "Kiambu collection point" },
      "destination_market": "Nairobi Gikomba",
      "risk_tier": "AT_RISK",
      "sequence": 1
    }
  ]
}
```
- **Query note (from §2.1):** a stop at a cooperative's collection point can bundle
  multiple farmers' shipments under one `cooperative_id` into a single pickup —
  the manifest should group by pickup location + cooperative, not list every
  individual farmer's shipment as a separate stop, or a driver's day gets needlessly
  fragmented. Individual-venture shipments stay one stop each, keyed on
  `submitted_by_user_id`.

### `POST /mobile/driver/stops/{shipment_id}/confirm`
```json
// Request
{ "confirmed_at": "2026-09-02T07:40:00Z", "location": { "lat": -1.31, "lon": 36.80 } }

// Response 200
{ "status": "delivered", "shipment_status": "IN_TRANSIT" }
```
- Same `client_id`-style idempotency isn't needed here since it's a state transition
  keyed on `shipment_id`, but the endpoint should still be safe to call twice (confirm
  is a no-op if already confirmed, not an error).

---

## 6. Notifications

### `POST /mobile/devices/register`
Register an FCM/APNs device token against the authenticated user, for push.
```json
{ "device_token": "...", "platform": "android" }
```

**Trigger conditions worth building first** (highest value, lowest complexity):
- Shipment crosses into `CRITICAL` risk tier after capture → notify the farmer.
- A driver's manifest changes after they've already synced it for the day → notify
  the driver, not just silently update server-side.

Push copy should go through the same locale lookup as `risk_label` in §4 — don't
hardcode English strings in the notification payload builder.

---

## 7. Locale

Given the farmer-cooperative user base, plan for `Accept-Language: sw` (Swahili) from
day one on any user-facing copy the *server* generates (risk labels, push text,
error messages). Raw data (crop names, market names) can stay as-is; it's the
generated sentences that need translation infrastructure, and it's much cheaper to
build that in now than retrofit it after `risk_label` strings are scattered across
the codebase.

---

## 8. SMS/USSD fallback (stretch, separate track)

Not a REST contract in the same sense, but worth scoping now so the backend doesn't
accidentally make it hard later:
- A shipment created via USSD session needs the same `client_id` idempotency
  mechanism — the USSD gateway will retry on timeout just like a mobile client will.
- The `/mobile/shipments/recommendation` response shape (§4) is already minimal enough
  to render as an SMS: `"Tomatoes, 340kg: AT_RISK. Sell within 24h. Best market:
  Nairobi Gikomba, 42km, ~KES 11,492."` — worth keeping that endpoint's output as the
  single source of truth for both the app badge and the SMS reply template, rather
  than building two separate summarization paths.

---

## 9. Resolved decisions (v0.2)

- **Ownership model**: both `COOPERATIVE` and `INDIVIDUAL` accounts are supported,
  user-selected at profile completion. See §2.1 for schema impact on shipments,
  produce, and the driver manifest query.
- **Photo storage**: local disk to start, targeting Oracle Cloud Free Tier hosting.
  See §3.2 for the resize/quota/serving-path implications this creates.
- **Sync persistence**: `/mobile/shipments/sync` writes to a `shipment_sync_staging`
  table, reconciled into `shipments` by a separate job rather than direct writes.
  See §3.1.

## 10. Open questions remaining

- **Cooperative join flow** (invite code vs. admin approval vs. open join) is
  explicitly deferred — §2.1 only specifies *creating* a new cooperative during
  profile completion, not joining an existing one. Needs its own small spec before
  the cooperative account type is fully usable in practice.
- **Reconciliation job cadence and failure visibility** — how often the staging→
  shipments promotion runs, and where `FAILED` reconciliation rows surface for an
  admin to act on (§3.1 suggests a web dashboard list, not yet speced).
- **Oracle Free Tier disk sizing** — worth a rough capacity estimate (shipments/day ×
  average compressed photo size × retention period) before launch, so the "when do we
  need to migrate off local disk" question has a concrete trigger rather than being
  discovered at the point the disk actually fills up.
- **Migration path off local disk** — not urgent now, but worth deciding *in
  principle* (Oracle's object storage vs. S3-compatible) so §3.2's path-not-blob
  storage decision is validated against where you'd actually migrate to.
