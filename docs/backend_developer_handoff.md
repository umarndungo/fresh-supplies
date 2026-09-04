# Fresh Supplies — Backend Developer Handoff

Purpose: what was built and what's next on `backend/` (FastAPI), against what spec, and enough
system context to vibecode accurately without inventing conventions that already
exist in the codebase or conflicting with the mobile/data-engine contracts other
developers are building against.

---

## 1. Project context (read first)

The backend is already stable: JWT auth (access token in body, refresh in httpOnly
cookie), `/produce` and `/shipments` CRUD, `/ml/predict-spoilage` and
`/ml/recommend-market` (now bearer-auth'd), clean architecture layering (api /
application / domain / infrastructure), PostgreSQL via async SQLAlchemy 2.0 +
Alembic. The `/mobile/*` routes are now fully implemented (see §2.1 and §6 below).
You are not starting from scratch — you're extending an established
pattern. The work below comes from two other specs already written this cycle:
the **Mobile API Contract v0.2** and the **frontend handoff notes** — both assume
the endpoints/behavior below exist. Build against those docs, not just this summary.

---

## 2. Deliverables — what "done" looks like

### 2.1 `/mobile/*` route namespace (highest priority — three other people are blocked on this)

> **Status: IMPLEMENTED** — All endpoints below are built and tested (31 tests passing).

Implement the endpoints specified in the Mobile API Contract v0.2:
- `POST /mobile/auth/otp/request`, `/otp/verify`, `/refresh` — phone/OTP login that
  terminates in the *same* JWT response shape as `/auth/login`, so downstream code
  never branches on login method.
- `POST /mobile/auth/complete-profile` — account-type selection (`COOPERATIVE` |
  `INDIVIDUAL`), creates a `cooperative_id` on the fly for new cooperatives. Joining
  an *existing* cooperative is explicitly out of scope for this pass — don't build
  invite/approval logic speculatively.
- `POST /mobile/shipments/sync` — batched, `client_id`-idempotent upsert. **Writes to
  a new `shipment_sync_staging` table, not directly to `shipments`** (see §2.2).
- `POST /mobile/shipments/photo-upload` — multipart, local disk storage (see §2.3).
- `GET /mobile/shipments/sync-status?since=` — delta pull for server-side changes.
- `GET /mobile/shipments/{id}/recommendation` — simplified wrapper around
  `predict-spoilage` + `recommend-market`: one risk tier, one action sentence, one
  top market, two alternates. Not the full ranked table.
- `GET /mobile/driver/manifest?date=` — grouped by pickup location + `cooperative_id`
  where applicable (a cooperative's collection point can bundle many farmers'
  shipments into one stop; individual-venture shipments stay one stop each).
- `POST /mobile/driver/stops/{shipment_id}/confirm` — idempotent state transition,
  safe to call twice.
- `POST /mobile/devices/register` — FCM/APNs token registration for push.

Full request/response JSON shapes are in the mobile contract doc — implement against
that exactly; if anything there is ambiguous or looks wrong given the actual DB
schema, flag it back rather than silently deciding differently.

### 2.2 Schema changes

> **Status: IMPLEMENTED** — Migration `0002_mobile_api.py` creates all new tables and columns.

- New `shipment_sync_staging` table: `client_id` (unique), raw payload columns,
  `sync_received_at`, `reconciliation_status` (`PENDING`/`RECONCILED`/`FAILED`),
  `reconciled_shipment_id` (nullable).
- New `cooperatives` table: `id`, `name`, `created_at`, admin `user_id`.
- Add to `shipments` and `produce`: `owner_type` (`COOPERATIVE`/`INDIVIDUAL`),
  `cooperative_id` (nullable FK), `submitted_by_user_id`.
- A **reconciliation job** (periodic task — APScheduler, a cron-triggered script, or
  a Celery/RQ worker if you want to introduce a task queue) that promotes
  `PENDING` staging rows into `shipments`, running `/ml/predict-spoilage` inline if it
  wasn't already computed at staging time. `FAILED` rows need to be queryable by an
  admin — a simple `GET /shipments/sync-issues` route for the web dashboard is enough
  for now, doesn't need a dedicated UI on your end.
- New Alembic migration(s) for all of the above. Remember the two documented gotchas:
  `%` needs escaping as `%%` in URL interpolation (already handled in `env.py`), and
  a literal `@` in a DB password must be URL-encoded (`%40`) in `DATABASE_URL`.

### 2.3 Photo storage — local disk, Oracle Free Tier target
- Store a resized/compressed version on upload (~1600px long edge, JPEG ~80 quality)
  server-side — don't trust the client to have done this consistently.
- Store a relative path/reference key in the DB, never raw bytes in a column, and
  never assume the storage backend won't change later — this is a deliberate
  disk-now-object-storage-later decision, so keep the storage access behind a small
  adapter/interface rather than scattering `open(path)` calls through the codebase.
- Serve photos through an **authenticated** route (`GET /shipments/{id}/photo`), not
  a static file path — respects the same RBAC as everything else.
- This is a known single-point-of-failure tradeoff on a free-tier VM — worth a line
  in whatever limitations doc the project keeps, not a silent assumption.

### 2.4 OTP delivery + rate limiting
- Rate-limit `/mobile/auth/otp/request` aggressively (e.g. 3/10min per number) — it's
  an open endpoint and the obvious abuse vector.
- SMS delivery provider: coordinate with the mobile+USSD developer before picking one
  — if USSD/SMS fallback also needs a gateway (Africa's Talking is the standard
  choice for Kenya), it may make sense to share one provider account/integration
  rather than standing up two.

### 2.5 A lower-trust auth path for USSD (coordinate with mobile+USSD dev)
USSD sessions are already phone-verified by the telco — OTP-over-SMS doesn't make
sense inside a USSD flow with a ~120–180 second session window. You'll likely need a
distinct, more limited auth mode (phone number + telco session token, no OTP round
trip) scoped narrowly to what USSD needs (submit a shipment, get a recommendation) —
**do not** reuse the full JWT/refresh contract for this; it's a different trust model
and should be recognizable as such in the code, not quietly bolted onto the OTP path.
Treat this as an open item to spec jointly with the mobile+USSD developer before
building, not something to guess at alone.

### 2.6 Test coverage

> **Current: 31 tests** (was 19, now 31). Added:
> - 8 mobile auth tests (OTP request/verify, refresh, complete-profile)
> - 7 mobile shipment tests (sync, photo, sync-status, recommendation)
> - 4 mobile driver tests (manifest, confirm)
> - 2 mobile device tests (register)
> - 4 i18n tests (risk labels, notification copy)

Current coverage (19 tests: model regression + `/ml` contract) is a good start but
thin. Priority additions:
- Auth flow tests (register/login/refresh/OTP) including the rate limiter.
- CRUD tests for `/produce`, `/shipments`, and the new `/mobile/*` routes —
  especially the idempotency behavior of `/mobile/shipments/sync` (duplicate
  `client_id` → `"duplicate"` status, not a second row) and the reconciliation job.
- A migration smoke test (`alembic upgrade head` on a clean DB) — this doesn't exist
  yet and is cheap insurance against migration drift.

### 2.7 Observability (currently absent)
Minimal but real: structured request logging, and error tracking (Sentry or
equivalent) — at minimum around the ML inference path and the reconciliation job,
since those are the two places a silent failure would be hardest to notice otherwise.

---

## 3. Explicitly out of scope this phase

- Cooperative *join* flow (invite code / approval) — only *creation* is in scope.
- Model registry/versioning for ML artifacts — flagged as a known limitation, not a
  deliverable here; don't build a bespoke versioning system speculatively.
- Bulk-loading data-engine synthetic shipments into the `produce` table.
- Any change to the ML training pipeline itself — that's the data engine developer's
  surface; if a backend need implies a training change, flag it, don't implement it.

---

## 4. AI context packet (for vibecoding)

```
PROJECT: Fresh Supplies backend — FastAPI, clean architecture (app/api, app/application,
app/domain, app/infrastructure, app/core), PostgreSQL via SQLAlchemy 2.0 async +
asyncpg, Alembic migrations, JWT auth (access token in response body, refresh token in
httpOnly cookie for web / response body for mobile), password hashing via passlib
pbkdf2_sha256 (not bcrypt — a prior bcrypt 5.x/passlib incompatibility caused a swap;
do not reintroduce bcrypt).

DO NOT invent schema or endpoint shapes. The mobile endpoints being built are specified
exactly in "Fresh Supplies — Mobile API Contract v0.2" — implement against that document's
JSON shapes verbatim. If a shape in that doc looks inconsistent with the existing DB
schema, say so explicitly rather than silently resolving the conflict.

Existing conventions to mirror, not reinvent:
- Repository pattern in app/infrastructure — new tables (cooperatives,
  shipment_sync_staging) get a repository following the same shape as the existing
  shipment/produce repositories, not a one-off query scattered in a route handler.
- ML inference already runs in a threadpool via app/application/ml_service.py with a
  cached model load — the reconciliation job's spoilage prediction should reuse this
  service, not reimplement model loading.
- Alembic gotchas: escape % as %% in URL interpolation; URL-encode @ as %40 in any
  DATABASE_URL with a literal @ in the password.

Domain facts affecting implementation:
- A shipment is "spoiled" when predicted loss > 15%.
- The ML model's ROC-AUC is ~0.87 on a synthetic validation set — deliberately not
  higher; a prior version hit 0.99 due to a label-circularity bug in the data engine's
  target construction, which has since been fixed and is now guarded by a regression
  test on the data-engine side. Do not "improve" accuracy on the backend by changing
  how predictions are used or thresholded without understanding why 0.99 was wrong.
- owner_type/cooperative_id/submitted_by_user_id are the new ownership columns —
  cooperative_id is nullable and only set when owner_type is COOPERATIVE.

When implementing a new /mobile/* route, state which existing route/service you're
mirroring the structure of before writing code.
```

---

## 5. Suggested build order

- [x] 1. Schema migrations (§2.2) — everything else depends on these existing first.
- [x] 2. `/mobile/auth/*` (OTP + complete-profile) — unblocks the mobile app's onboarding.
- [x] 3. `/mobile/shipments/sync` + staging table + reconciliation job — the core value
       surface; unblocks offline capture testing end to end.
- [x] 4. `/mobile/shipments/{id}/recommendation` — thin wrapper, quick once §3 exists.
- [x] 5. `/mobile/shipments/photo-upload` — can happen in parallel with 3–4.
- [x] 6. `/mobile/driver/manifest` + stop confirmation.
- [x] 7. `/mobile/devices/register` + notification triggers.
- [ ] 8. USSD-specific lower-trust auth (§2.5) — coordinate timing with the mobile+USSD dev,
       since it's only needed once that channel is actually being built.

**What's next:** Item 8 (USSD auth) remains, plus observability (§2.7), admin sync-issues
endpoint, and reconciling SMS provider integration (see §7).

---

## 6. What's been built — file inventory

### New files
- `app/api/routes/mobile_auth.py` — OTP request/verify, mobile refresh, complete-profile
- `app/api/routes/mobile_shipments.py` — batch sync, photo upload, sync-status, recommendation
- `app/api/routes/mobile_driver.py` — driver manifest, stop confirmation
- `app/api/routes/mobile_devices.py` — FCM/APNs device registration
- `app/application/mobile_schemas.py` — all mobile Pydantic request/response schemas
- `app/application/otp_service.py` — OTP generation, rate-limiting, verification
- `app/application/mobile_auth_service.py` — phone login, refresh, profile completion
- `app/application/mobile_shipment_service.py` — staging sync, photo storage, sync-status
- `app/application/mobile_recommendation_service.py` — simplified risk+market
- `app/application/reconciliation_service.py` — staging→shipments background job
- `app/application/device_service.py` — device token registration
- `app/application/driver_service.py` — manifest + stop confirm logic
- `app/infrastructure/otp_repository.py` — OTP CRUD
- `app/infrastructure/cooperative_repository.py` — cooperative CRUD
- `app/infrastructure/shipment_sync_repository.py` — staging table CRUD
- `app/infrastructure/device_token_repository.py` — device token CRUD
- `app/infrastructure/driver_repository.py` — manifest queries
- `app/core/i18n.py` — en/sw translation infrastructure
- `alembic/versions/0002_mobile_api.py` — full schema migration
- `tests/test_mobile_auth.py` — 8 tests
- `tests/test_mobile_shipments.py` — 7 tests
- `tests/test_mobile_driver.py` — 4 tests
- `tests/test_mobile_devices.py` — 2 tests
- `tests/test_i18n.py` — 4 tests

### Modified files
- `app/domain/entities.py` — +5 enums, +User fields, +4 new dataclasses
- `app/domain/repositories.py` — +6 new ABCs, +3 new UserRepo methods
- `app/infrastructure/models.py` — +4 new tables, +UserModel/ShipmentModel fields
- `app/infrastructure/user_repository.py` — +3 new methods, updated mapper
- `app/application/schemas.py` — UserOut with phone/account fields
- `app/core/config.py` — +7 new settings (OTP, photos, reconciliation)
- `app/api/deps.py` — +6 new DI factories
- `app/api/router.py` — +4 mobile route registrations
- `requirements.txt` — +Pillow, +apscheduler
- `tests/test_ml_api.py` — fixed for new User entity fields

---

## 7. Open questions to raise, not guess on

- **Cooperative join flow:** Still open. Invite code / approval logic is explicitly out
  of scope for this phase but remains a known gap for post-MVP.
- **Reconciliation job cadence:** The service is built (`reconciliation_service.py`)
  but scheduling is not wired up yet. Needs APScheduler integration or an external
  cron job — every N minutes vs. triggered. Affects how "instant" a risk-tier badge
  feels vs. how much load the job adds.
- **SMS/OTP provider:** Still needs real integration (Africa's Talking / Twilio). The
  OTP service is structured for easy swap — confirm with the mobile+USSD developer
  before integrating, in case one gateway account can serve both OTP and USSD/SMS needs.
- **Admin sync-issues endpoint:** Where `FAILED` reconciliation rows surface for an
  admin — worth a quick product decision before building the query, even if the UI
  for it comes later.
