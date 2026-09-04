# Fresh Supplies — Web Frontend Developer Handoff

Purpose of this doc: give the frontend developer everything needed to build the
remaining web app — what to build, in what order, against what backend contract,
and enough system context to paste into an AI coding assistant (Claude Code, Cursor,
etc.) and get accurate, non-hallucinated output on the first pass.

---

## 1. Project context (read first)

Fresh Supplies predicts post-harvest spoilage risk for East African perishable-crop
shipments and recommends which market to sell to for the best revenue retained
(`qty × price × (1 − spoilage%)`). Three subsystems exist:

- **`post_harvest_data_engine/`** — Python ETL + ML training. Not your concern day to
  day; it produces artifacts the backend loads.
- **`backend/`** — FastAPI, already built and stable. This is your API. Clean
  architecture (api / application / domain / infrastructure layers) — you don't need
  to touch it, only consume it.
- **`src/`** — the Next.js 16 frontend you're extending. Auth, dashboard shell, and
  Shipment CRUD already exist. **This handoff is about everything after that.**

**Who actually uses this web app:** logistics managers, market analysts, and farmer
cooperative admins — desk/office users on real screens, not the farmer-in-a-field
persona (that's a separate mobile/WhatsApp channel being scoped elsewhere). Build for
data density and clarity, not for one-glance simplicity.

---

## 2. Deliverables — what "done" looks like

In priority order (highest business value / lowest effort first):

### 2.1 Wire the ML endpoints into the shipment flow — **do this first**
The backend already exposes `/ml/predict-spoilage` and `/ml/recommend-market`, but
nothing in the frontend calls them yet. This is the single biggest gap between what
the product is supposed to do and what a user can currently see. When a shipment is
created or viewed:
- Call `predict-spoilage`, display a **risk-tier badge** (Fresh / At-Risk / Critical)
  with color coding, inline on the shipment card and detail view.
- Call `recommend-market`, show a **ranked market table** (market name, distance,
  price/kg, revenue retained) on the shipment detail page.
- Both endpoints require bearer auth now (recently added) — make sure your API client
  attaches the token to these calls like it does for `/produce` and `/shipments`.

### 2.2 Produce Inventory UI
Mirror the existing Shipment CRUD pattern exactly — same table/form/modal conventions,
same TanStack Query + zod + react-hook-form approach already in the codebase. Backend
route: `GET/POST/PATCH/DELETE /produce`. Note the `commodity_class` enum
(PERISHABLE/STAPLE) on this model — surface it as a filter, not just a display field.

### 2.3 GIS map view
Plot the 10 fixed Kenyan market destinations (Nairobi Gikomba, Nakuru Wakulima,
Mombasa Kongowea, Kisumu, Eldoret, Thika, Kakamega, Meru, Naivasha, Bomet) and a given
shipment's recommended route. Use Leaflet or Mapbox GL — whichever the dev is faster
in, no strong preference. This is also your best demo/investor-facing screen, so it's
worth polish time.

### 2.4 Analytics dashboards
Spoilage trend over time, revenue-retained by crop, risk-tier distribution. Data
source: the same shipment + ML response data already flowing through the app — no new
backend work needed, this is a visualization layer on existing data.

### 2.5 Role-differentiated dashboards
RBAC exists on the backend (ADMINISTRATOR, LOGISTICS_MANAGER, FARMER_COOPERATIVE,
MARKET_ANALYST) but the frontend currently only gates *routes*, not *views*. Build
actually distinct dashboard layouts per role:
- **Logistics Manager**: fleet-wide risk overview, all shipments, map view.
- **Market Analyst**: full ranked market tables, price trends, analytics-heavy.
- **Farmer Cooperative**: their own shipments only, simplified recommendation view
  (closer to the one-glance pattern — this is the one role where density should drop).

### 2.6 i18n — Swahili
Given the farmer-cooperative role, plan for `next-intl` or similar from the start of
any new screen work, not retrofitted later. Server-generated copy (risk labels,
recommendation sentences) should go through a translation lookup table, not be
hardcoded English strings scattered through components.

**Explicitly out of scope for this phase** (per the project's own status doc): bulk-
loading data-engine shipments into the `produce` table, and any changes to the ML
model or training pipeline. If either seems necessary to finish a screen, flag it
rather than working around it.

---

## 3. Product / API spec

### Auth (already implemented — reference only)
- `POST /auth/register`, `/login`, `/refresh`, `/logout` — JWT access token in
  response body, refresh token in httpOnly cookie.
- `GET /auth/me` — current user + role.
- Auth contract: `{ data: { accessToken, expiresIn, user } }` — the existing frontend
  auth code already matches this; reuse its client/interceptor, don't rebuild it.

### Core CRUD (partially implemented)
| Route | Status |
|---|---|
| `/shipments` (GET/POST/PATCH/DELETE) | ✅ built |
| `/produce` (GET/POST/PATCH/DELETE) | ❌ your build |

### ML endpoints (built on backend, **not yet wired into frontend**)
| Route | Auth | Notes |
|---|---|---|
| `POST /ml/predict-spoilage` | bearer | Returns spoilage probability + risk tier |
| `POST /ml/recommend-market` | bearer | Returns all 10 markets ranked by revenue retained |

Ask the backend dev (or check `app/application/schemas`) for the exact request/response
JSON shapes before building — don't guess field names; get them from the Swagger docs
at `/docs` on a running backend instance, since that's always ground truth.

### Environment
- `NEXT_PUBLIC_API_URL` (default `http://localhost:8000/api/v1`) — never hardcode
  localhost in component code; everything routes through this env var already.

### Known backend conventions worth knowing about
- KPI spoilage threshold: a shipment is "spoiled" when estimated loss > 15% — this is
  the basis for whatever risk-tier badge coloring/copy you write.
- The ML model's ROC-AUC is ~0.87 on a *synthetic* dataset — when writing copy near
  these predictions (tooltips, disclaimers), don't imply more certainty than that;
  a small "prediction, not guarantee" affordance is appropriate on the risk badge.
- Market prices are synthetic-but-calibrated, not live data — if you add any "as of"
  or "live price" language anywhere in the UI, it would be inaccurate; keep copy
  neutral ("estimated price/kg").

---

## 4. Design system guidance

We reviewed a mature fintech design system (onboarding, wallet, KYC, savings flows)
as a style reference. Verdict: **borrow the component patterns, not the screen
density** — this app's primary users (logistics managers, analysts) can handle more
information per screen than a fintech consumer app, but the *component discipline* is
worth copying directly:

- **One primary button style everywhere** — full-width pill, single brand color fill,
  bold white label. Don't let it drift per-screen.
- **A single reusable `StatusBadge`/tile pattern** for risk tiers and transaction-like
  lists (shipment status, market rank) — build once, reuse for shipments, produce,
  and analytics rows alike.
- **Charts with a shaded-gradient line pattern** (recharts, since that's already in the
  stack per `package.json`) for trend visualizations — consistent look across
  analytics screens.
- **Progress/step patterns** for any multi-step flow (e.g. if produce-intake or bulk
  actions get a wizard) — thin segmented top bar for linear flows, circular step
  counter for verification-style flows. Pick one pattern per flow type and stay
  consistent.
- Build a small internal `design-system/` or `components/ui/` extension (you already
  have shadcn/ui as a base) for semantic colors — risk tiers (Fresh/At-Risk/Critical)
  aren't in a default theme and should be defined once, not re-picked per component.

---

## 5. AI context packet (for vibecoding)

Paste the block below into your AI assistant of choice at the start of a session, or
keep it as a system/project prompt if your tool supports one. It's written to prevent
the two most common AI-coding failure modes on a project like this: inventing API
shapes that don't exist, and rebuilding patterns that already exist elsewhere in the
codebase.

```
PROJECT: Fresh Supplies — web frontend (Next.js 16, App Router, React 19, TypeScript,
Tailwind CSS v4, shadcn/ui, TanStack Query, axios, zod + react-hook-form).

This frontend already has: JWT auth (login/register, refresh-cookie flow, protected
routes, RBAC route gates), a dashboard shell (sidebar/topbar/breadcrumbs/notifications/
profile menu/theme toggle), and full Shipment CRUD. DO NOT rebuild any of these —
extend the existing patterns. Before creating a new component, check whether an
equivalent already exists for Shipments and mirror its structure for new features
(Produce, etc.) rather than inventing a new pattern.

Backend: FastAPI, base URL from env NEXT_PUBLIC_API_URL (default
http://localhost:8000/api/v1). Auth response shape: { data: { accessToken, expiresIn,
user } }, access token in body, refresh token in httpOnly cookie. Never hardcode a
base URL or port in component code.

DO NOT invent API request/response field names. If you don't have the exact schema
for an endpoint, say so explicitly and ask for the Swagger/OpenAPI output from
/docs, or ask to see the relevant Pydantic schema — do not guess and produce plausible-
looking-but-wrong field names, since this causes silent runtime bugs against the real
backend.

Endpoints relevant to current work:
- GET/POST/PATCH/DELETE /produce (bearer auth) — mirror the existing /shipments
  frontend pattern exactly (same table/form/modal/query conventions).
- POST /ml/predict-spoilage (bearer auth) — returns spoilage probability + risk tier
  (Fresh/At-Risk/Critical). Get exact schema from /docs before wiring.
- POST /ml/recommend-market (bearer auth) — returns markets ranked by revenue
  retained (qty × price × (1 − spoilage%)). Get exact schema from /docs before wiring.

Domain facts that affect UI copy:
- A shipment is "spoiled" when predicted loss > 15% — this is the basis for risk-tier
  thresholds/coloring.
- Market prices are synthetic-but-calibrated estimates, not live data — never use
  "live price" or "as of [time]" language in copy.
- The ML model has real but imperfect accuracy (~0.87 ROC-AUC on validation) — avoid
  copy that implies certainty ("will spoil"); prefer "predicted risk," "estimated."

Design conventions: single pill-shaped primary button style app-wide; a shared
status-badge component for risk tiers and status indicators, not one-off styled divs
per screen; recharts for all trend visualizations (already a dependency) with a
shaded-gradient line style; semantic risk-tier colors defined once in the theme, not
re-picked per component.

Users are logistics managers, market analysts, and farmer-cooperative admins on
desktop/tablet — not a farmer-in-field mobile persona. Screens can be information-
dense; that's appropriate for this audience.

When building a new screen, first state which existing component/pattern you're
mirroring and which parts are genuinely new, before writing code.
```

---

## 6. Suggested build order

1. ML integration into existing shipment views (§2.1) — no new screens, highest
   visible impact.
2. Produce Inventory CRUD (§2.2) — mechanical, mirrors existing Shipment pattern.
3. Map view (§2.3) — new dependency (Leaflet/Mapbox), moderate effort, high demo value.
4. Analytics dashboards (§2.4) — pure visualization layer on data already flowing.
5. Role-differentiated dashboard layouts (§2.5) — depends on 1–4 existing to compose.
6. i18n (§2.6) — ideally threaded through as 1–5 are built, not bolted on after.

---

## 7. Open questions for the frontend dev to raise, not guess on

- Exact request/response schema for both `/ml` endpoints (pull from `/docs`, don't
  infer from this document).
- Whether `produce` records need a `cooperative_id`-style grouping for multi-user
  cooperatives, which would affect the Farmer Cooperative dashboard's data scoping.
- Map tile provider choice (Leaflet + OpenStreetMap is free/simple; Mapbox GL has
  nicer styling but needs an API key/billing) — a product decision, not a dev default.
