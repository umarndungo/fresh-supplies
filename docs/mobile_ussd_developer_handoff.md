# Fresh Supplies — Mobile + USSD Developer Handoff

Purpose: what to build for the field-facing farmer/driver channels — the app and the
USSD/SMS fallback — against the Mobile API Contract v0.2, with enough design and
system context to vibecode accurately.

---

## 1. Project context (read first)

> **Backend status: all `/mobile/*` endpoints are implemented and tested.** The
> backend developer has completed all endpoints specified in the Mobile API Contract
> v0.2 — OTP auth, shipment sync, photo upload, recommendation, driver manifest,
> stop confirmation, and device registration. The Flutter developer can build against
> these endpoints now; they are live at `/api/v1/mobile/*`.

Two channels, one backend contract. The **app** (Flutter, based on the design-system
review already done for this project) serves drivers/logistics primarily and farmers
who have smartphones; **USSD/SMS** exists because a meaningful share of the actual
target users — farmers in rural Kenya — may not have a reliable smartphone or data
plan. Both channels talk to the same `/mobile/*` backend surface (see the Mobile API
Contract v0.2) — you are not building two separate backends' worth of logic, you're
building two different front doors onto the same sync/recommendation endpoints.

**Who uses which channel:**
- **App, farmer flow**: one-glance risk tier + recommendation, offline-first capture.
- **App, driver flow**: manifest, route, stop confirmation — denser, more list/table
  UI, closer to the fintech-style component patterns already reviewed for this
  project (transaction-tile-style stop lists, stat cards, progress indicators).
- **USSD/SMS**: text-only equivalent of the farmer flow — capture a shipment, get a
  recommendation, nothing else. No manifest, no photos, no dashboards.

---

## 2. Deliverables — App (Flutter)

### 2.1 Auth + onboarding
**Backend i18n is ready** — the backend now has `app/core/i18n.py` with `en` and `sw`
translations for risk labels and notification copy. The recommendation endpoint
accepts `Accept-Language` query parameter (default `en`). Send `Accept-Language: sw`
from the Flutter app to get Swahili risk labels and notification text from the API.
Don't maintain a separate client-side copy of these strings — render what the API
returns.

- Phone + OTP login (`/mobile/auth/otp/request`, `/otp/verify`) — reuse the
  passcode-keypad pattern from the design-system reference (custom numeric grid, not
  the OS keyboard) for a consistent branded PIN-entry feel.
- Account-type selection screen (`/mobile/auth/complete-profile`) — `COOPERATIVE` vs
  `INDIVIDUAL`, with cooperative name entry if creating a new one. **Joining an
  existing cooperative is out of scope this phase** — don't build a speculative
  invite-code UI for it.
- Store the refresh token in secure device storage (`flutter_secure_storage`), never
  plain shared preferences.

### 2.2 Offline shipment capture — the core surface
> The sync endpoint (`POST /mobile/shipments/sync`) returns `risk_tier` inline per
> item — computed against the staged record synchronously. The reconciliation job
> (`app/application/reconciliation_service.py`) promotes staging rows to the
> canonical `shipments` table periodically. The Flutter app should handle the mixed
> partial-failure response where some items succeed and others error.

- Local queue (recommend `sqflite` or `Hive` for the offline store) — every capture
  writes locally first, syncs opportunistically.
- Generate a `client_id` (UUID v4) **on-device at capture time**, not at sync time —
  this is the idempotency key the backend uses to dedupe retried syncs, so it must be
  stable across retries of the same local record.
- Batch sync (`POST /mobile/shipments/sync`) on a background trigger
  (`workmanager` + connectivity change via `connectivity_plus`), not only on manual
  pull-to-refresh — the whole point is that a farmer can capture all day in a dead
  zone and have it sync automatically once back in range.
- Handle the **mixed partial-failure response** correctly — some shipments in a batch
  can succeed while others error; update local queue state per-item, don't treat the
  batch as atomic.
- Compress/resize photos on-device before upload as a courtesy (saves the user's
  data), but don't rely on this alone — the backend also resizes server-side.
- Show the risk-tier badge **immediately** from the sync response (it's computed
  against the staged record synchronously) — don't make the user wait for background
  reconciliation to see a result.

### 2.3 Simplified recommendation view
> The recommendation endpoint is at `GET /mobile/shipments/{id}/recommendation`
> and accepts query params: `crop`, `quantityKg`, `lat`, `lon`, `Accept-Language`.
> It returns `risk_tier`, `risk_label` (translated), `recommended_market`, and
> `alternate_markets` (top 2).

`GET /mobile/shipments/{id}/recommendation` → one risk tier badge, one plain-language
action sentence, one primary recommended market, two alternates behind a "see other
options" tap. This is the farmer-facing screen — keep it to the one-number/one-
sentence/one-action density discussed earlier, not the driver/analyst density.

### 2.4 Driver flow
- `GET /mobile/driver/manifest?date=` — list/calendar view, reuse the
  fintech-style transaction-tile pattern (icon + title/subtitle + trailing status)
  for each stop, with risk-tier color coding.
- `POST /mobile/driver/stops/{shipment_id}/confirm` — safe to tap twice (idempotent
  on the backend), so don't over-engineer double-tap prevention client-side beyond
  normal UX polish.
- Cooperative pickups are already grouped server-side into one stop per collection
  point — don't re-fragment them into per-farmer stops in the UI.

### 2.5 Notifications
> Device registration is implemented at `POST /mobile/devices/register` — send
> `{"deviceToken": "...", "platform": "android"|"ios"}` after login. Push
> notification triggers (CRITICAL tier change, manifest update) are not yet
> implemented server-side — the device registration and i18n infrastructure is
> ready, but the trigger logic is a follow-up item.

`POST /mobile/devices/register` on login; handle at minimum: shipment crosses into
`CRITICAL` risk tier, and manifest changes after a driver has already synced for the
day.

### 2.6 Localization
Swahili from the start, not retrofitted — `flutter_localizations` + `intl`, with
server-generated strings (risk labels, recommendation sentences) treated as data
from the API, not hardcoded — the backend already plans to key these off
`Accept-Language`, so the app just needs to send that header and render whatever
comes back rather than maintaining its own duplicate copy of those strings.

---

## 3. Deliverables — USSD/SMS fallback

This is a genuinely different interaction model, not a stripped-down app screen —
design it as its own conversation flow.

### 3.1 Session flow (USSD)
A typical session (via a gateway like Africa's Talking) has a ~120–180 second window
and no persistent state beyond the session — plan the menu tree short:
1. Language select (English/Swahili) — first screen, remembered for SMS follow-ups
   to the same number if possible.
2. Crop select (from the fixed 9-crop list — reuse `crops.yaml`'s list via the
   backend, don't hardcode it here either).
3. Quantity entry (numeric).
4. Location — **USSD has no GPS.** Use a manual nearest-collection-point or
   nearest-town selection list instead of lat/lon; coordinate with the backend on
   what location granularity the recommendation endpoint can actually work with at
   that resolution.
5. Submit → immediate reply with risk tier + recommended market, reusing the exact
   copy shape from `/mobile/shipments/{id}/recommendation` (§4 of the mobile
   contract already scoped this endpoint's output to be SMS-renderable, e.g.
   *"Tomatoes, 340kg: AT_RISK. Sell within 24h. Best market: Nairobi Gikomba, 42km,
   ~KES 11,492."*) — don't build a second summarization template; call the same
   endpoint logic the app uses.

**This works because of a specific backend design choice worth knowing about**: the
recommendation is computed against the *staged* record immediately, before the slower
shipments-table reconciliation runs — so a USSD session can get a real-time answer
inside its short session window even though the official shipment record settles a
few minutes later in the background.

### 3.2 Auth model — different from the app
USSD sessions are already phone-verified by the telco. **Don't reuse the OTP/JWT
flow** — there's no time for an OTP round trip inside a USSD session, and the trust
model is different (carrier-attested number vs. app-level credential). This needs a
narrower, phone-number-scoped auth path on the backend, limited to "submit a
shipment, get a recommendation" — nothing else. This is called out as a joint
open item with the backend developer; don't build against a guessed version of it.

### 3.3 SMS
- Outbound: reuse the same recommendation copy for any async SMS notifications
  (e.g. "your shipment synced, here's the result" for a farmer who submitted via app
  but was offline when the prediction came back).
- Inbound (stretch): a structured SMS format (e.g. `CROP QTY LOCATION`) as a fallback
  for markets without USSD gateway coverage — lower priority than the USSD flow
  itself, only worth building if USSD gateway coverage turns out to be a real gap in
  practice.

---

## 4. Design guidance

The fintech-style reference reviewed earlier is the right source for **component
patterns** (single pill-button style, transaction-tile pattern for lists, progress
indicators, passcode keypad), applied selectively:
- **Driver screens** can use that reference's actual density — manifests, stop
  lists, and stat cards translate directly.
- **Farmer capture/recommendation screens** should be much sparser — big risk-tier
  number/badge, one sentence, one button. Resist pulling in extra chart/stat
  components here just because they exist in the shared widget library.
- Build a small internal `design_system/` package (as discussed) with a
  `ThemeExtension` for the semantic risk-tier colors (Fresh/At-Risk/Critical aren't
  in Flutter's default `ColorScheme`) — define once, reuse everywhere, including in
  the driver manifest's status tiles.
- Test contrast and legibility **in direct sunlight** on a real device before
  finalizing the farmer-facing color/typography choices — this app will genuinely be
  used outdoors.

---

## 5. AI context packet (for vibecoding)

```
PROJECT: Fresh Supplies mobile app — Flutter, targeting the farmer/driver field
persona. Backend contract: "Fresh Supplies — Mobile API Contract v0.2" — implement
against its exact JSON request/response shapes, do not invent field names.

Core architectural requirement: OFFLINE-FIRST. Every shipment capture writes to a
local store (sqflite/Hive) before any network call. A client-generated UUID v4
(`client_id`), created at capture time and stable across retries, is the idempotency
key the backend uses to dedupe — never regenerate it on retry, never sync without it.

Sync is a batched POST (/mobile/shipments/sync) with a MIXED partial-failure response
— per-item, not all-or-nothing. Update local record state per item based on the
response array; do not treat the whole batch as succeeded or failed together.

Two distinct auth models exist and must not be conflated:
1. App: OTP -> JWT (access token body, refresh token body on mobile, stored in
   flutter_secure_storage) — full auth, used for everything in the app.
2. USSD: phone-number/telco-session-scoped, no OTP round trip, narrow permission
   scope (submit + recommend only) — a SEPARATE, more limited backend auth path,
   not a reuse of the JWT flow. If building USSD integration, confirm the actual
   endpoint/auth shape with the backend developer rather than assuming it mirrors
   the app's OTP flow.

Account model: user selects account_type (COOPERATIVE or INDIVIDUAL) at profile
completion. Cooperative JOIN flow (as opposed to creation) is out of scope this
phase — do not build UI for it speculatively.

Design system: two density tiers by user role. Driver/logistics screens can be
information-dense (manifest lists, stat cards, multi-field forms) reusing patterns
from the reviewed fintech-style reference (pill buttons, transaction-tile list rows,
step-progress headers, custom passcode keypad). Farmer-facing capture/recommendation
screens must stay minimal: one risk-tier badge, one action sentence, one primary
recommended market. Do not add secondary charts/stats to farmer screens just because
matching widgets exist in the shared component library.

Localization: Swahili + English from the start via flutter_localizations + intl.
Server-generated copy (risk labels, recommendation sentences) comes from the API via
Accept-Language — render what the API returns, do not maintain a separate hardcoded
copy of those specific strings client-side (static UI chrome strings are fine to
localize normally).

When implementing a new screen or sync behavior, state which existing pattern
(offline queue handling, auth flow, design-system component) you're reusing before
writing code, and flag explicitly if a required backend endpoint/shape isn't yet
confirmed rather than guessing its contract.
```

---

## 6. Suggested build order

The backend endpoints are all implemented. The Flutter developer can proceed with:
1. Auth + onboarding (§2.1) — backend ready
2. Offline capture + sync (§2.2) — backend ready
3. Recommendation view (§2.3) — backend ready
4. Driver manifest + confirmation (§2.4) — backend ready
5. Notifications (§2.5) — device registration ready, trigger logic pending
6. USSD flow (§3) — backend auth path still needs spec (lower-trust model)
7. Localization (§2.6) — backend i18n ready, Flutter localization needed

---

## 7. Open questions to raise, not guess on

- Confirm the USSD/SMS gateway provider (Africa's Talking is the standard Kenya
  choice) and its session time limit in practice — affects how short the USSD menu
  tree needs to be.
- What location granularity works for a USSD user with no GPS — nearest town? Named
  collection points only? Needs a joint decision with the backend developer, since
  it affects what the recommendation endpoint can actually compute from.
- Confirm the lower-trust USSD auth shape with the backend developer (§3.2) before
  building against it — this is explicitly not specified yet in the mobile contract.
