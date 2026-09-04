# Fresh Supplies — Deployment Strategy & DevOps/Integration Notes

Scope: how the four subsystems (data engine, backend, web frontend, mobile+USSD) get
built, deployed, and kept working together, given the Oracle Cloud Free Tier hosting
target already decided for the backend.

---

## 1. Important update on the hosting assumption — read this first

Oracle changed the Always Free Ampere A1 allowance from **4 OCPUs / 24GB RAM down to
2 OCPUs / 12GB RAM**, effective June 15, 2026 — enacted with no blog post or customer
notification, discovered by users when instances got shut down or resized. The two
free AMD Micro VMs (1/8 OCPU, 1GB RAM each) still exist separately and are
unaffected, but they're too small for this workload on their own.

Two implications for planning:
1. **Size for 2 OCPU / 12GB, not 4/24** — cut your resource-sizing assumptions in
   half from what older Oracle documentation or tutorials describe.
2. **Free-tier limits on this provider can change without notice.** This isn't a
   one-time gotcha, it's a standing operational risk — build the deployment so that
   moving off Oracle later (or scaling up on Oracle) is a config change, not a
   rearchitecture. Everything below is written with that portability in mind
   (containerized services, externalized config, no Oracle-specific service
   dependencies beyond compute + block storage).

Also worth independently re-verifying current published limits (compute, the 200GB
block storage / 10GB object storage figures) at the point you actually provision,
since Oracle's own docs are the only source that updates in real time.

---

## 2. Environment strategy

Three environments, kept deliberately simple given team size and free-tier
constraints:

| Environment | Purpose | Where |
|---|---|---|
| **Local** | Everyone's dev machine | Docker Compose, mirrors prod services |
| **Staging** | Integration point all four subsystems point at before prod | Same Oracle VM as prod, separate Docker Compose stack + separate DB, OR a second free-tier AMD micro VM if isolation is worth the extra setup |
| **Production** | Live | Oracle Ampere A1 VM (2 OCPU/12GB) |

Given free-tier constraints, staging-on-the-same-VM (different port, different DB
name, different `.env`) is the pragmatic default — full environment isolation would
need a second always-on compute instance, which is a real cost/complexity tradeoff to
make deliberately, not default into.

---

## 3. Infra layout (single Oracle Ampere A1 VM, 2 OCPU / 12GB)

```
┌─────────────────────────────────────────────┐
│  Oracle Ampere A1 VM (Ubuntu, 2 OCPU/12GB)   │
│                                               │
│  Caddy (reverse proxy + auto TLS)            │
│    ├─ api.freshroute.<domain>  → backend     │
│    └─ (frontend origin, if self-hosted here) │
│                                               │
│  Docker Compose stack:                       │
│    ├─ backend (FastAPI/uvicorn)              │
│    ├─ postgres (persistent volume)           │
│    ├─ reconciliation worker (§ below)        │
│    ├─ reconciliation worker (app/application/reconciliation_service.py —
│    │   promotes staging→shipments, currently needs manual/cron trigger,
│    │   not yet a long-lived worker process)
│    └─ [staging stack, separate compose file] │
│                                               │
│  Block volume mount:                         │
│    ├─ /data/photos   (shipment photo storage)│
│    └─ /data/pg       (Postgres data dir)     │
│                                               │
│  Model artifacts: /data/models/<version>/    │
│    (produced by data engine, copied in — see │
│     §7 for the actual promotion mechanism)   │
└─────────────────────────────────────────────┘
```

- **Caddy over Nginx** for the reverse proxy — automatic Let's Encrypt TLS with
  zero manual cert management, one less thing to babysit on a small team.
- **Everything containerized** (backend, Postgres, reconciliation worker) so the
  whole stack is portable off Oracle if/when needed — `docker compose up` should
  work identically on any VM.
- **Data engine does NOT run on this VM as a long-lived service.** It's a periodic
  batch job (retrain, re-ingest) — run it on a schedule (cron or GitHub Actions
  scheduled workflow) either on the same VM in its own container, or off-box
  entirely (a GitHub Actions runner, since training doesn't need to be co-located
  with serving) and have it push artifacts to the VM afterward. This keeps the
  always-on VM's resource budget dedicated to serving traffic, not retraining.

---

## 4. Frontend deployment — don't put this on the Oracle VM

Recommend **Vercel's free tier** for the Next.js frontend instead of self-hosting on
the same constrained VM:
- Next.js is Vercel's native target — zero-config builds, preview deployments per PR,
  and it doesn't compete with the backend for the VM's limited 12GB RAM.
- Keeps the free-tier VM's resource budget entirely for backend + Postgres + photo
  storage, which is the part actually sensitive to the recent Oracle capacity cut.
- CORS: set `FRONTEND_ORIGIN` on the backend to the Vercel deployment URL(s) —
  already an existing config key per the project's own conventions.

If there's a strong reason to keep everything on one provider, self-hosting the
frontend on the same VM behind Caddy is possible, but budget RAM carefully — Next.js
SSR plus FastAPI plus Postgres plus the reconciliation worker on 12GB is tight.

---

## 5. Mobile app distribution

- **Internal testing first**: Android via Play Console's internal testing track,
  iOS via TestFlight — both support fast iteration without public review delay.
- **Flutter build config**: separate `--dart-define` flavors (or Flutter flavors
  proper) for `API_BASE_URL` per environment (local/staging/prod) — never hardcode
  the API host in the app, mirroring the "no hardcoded localhost" rule already
  established for the web frontend.
- **CI builds**: GitHub Actions with `flutter build apk`/`flutter build ios` on tag
  push, uploading to Play Console/TestFlight via `fastlane` once the team is ready
  for that automation — manual builds are fine for the first several iterations,
  don't over-invest in release automation before there's a release cadence to
  automate.

---

## 6. USSD/SMS gateway integration

- Set up an **Africa's Talking sandbox account** early, in parallel with the mobile
  developer's build — the sandbox lets you test USSD session flows against a
  simulator without needing a live shortcode, and this is usually the longest-lead-
  time external dependency (shortcode provisioning/approval can take real calendar
  time), so start it well before the flow is code-complete.
- The gateway calls your backend's USSD-specific endpoint over a webhook — this
  needs to be reachable from the public internet even in staging, so make sure
  staging is also behind Caddy/TLS on a real domain, not `localhost`-only.
  - Keep sandbox and production gateway credentials in clearly separate secrets (see
  §8) — a sandbox session hitting a production number, or vice versa, is an easy and
  embarrassing mistake to make once and should be structurally hard to make twice.

> **OTP delivery dependency:** The mobile auth flow generates OTP codes and stores
> them in the `otp_codes` table, but SMS delivery is not yet integrated. This needs
> an Africa's Talking or Twilio integration in `app/application/otp_service.py`
> before real users can log in via phone. The gateway setup should happen in
> parallel with the mobile app build.

---

## 7. CI/CD pipeline

One GitHub Actions workflow per subsystem (they can live in one monorepo or separate
repos — this doc assumes monorepo given the existing project layout, adjust paths if
split):

**Backend (`backend/`)**
1. On PR: lint, run pytest suite (31 tests — including mobile auth, shipment sync,
   driver manifest, device registration, and i18n tests), spin up a throwaway
   Postgres service container for integration tests.
2. On merge to `main`: build Docker image, push to a registry (GitHub Container
   Registry is free and simple), SSH/deploy to the Oracle VM (or trigger a `docker
   compose pull && up -d` via a small deploy script) — **run `alembic upgrade head`
   as an explicit, logged step before restarting the app container**, never silently
   inside app startup, so a bad migration is visible in the deploy log, not buried.

**Data engine (`post_harvest_data_engine/`)**
1. On PR: run the full pytest suite — **explicitly assert the model-regression AUC
   ceiling test passes** (this is the guard against the label-circularity bug
   recurring; it should be impossible to merge a change that silently disables or
   loosens it without that being visible in a diff).
2. On a schedule (not on every merge — retraining isn't free, run it deliberately):
   retrain, version the artifact (per the data-engine handoff's §2.2 versioning
   scheme), and push the new artifact + metadata to wherever the backend picks it up
   from (§ below).
3. Report the AUC number in the workflow output/PR comment on every run, not just
   pass/fail — a passing-but-degraded number should be visible, not hidden behind a
   green check.

**Web frontend (`src/`)**
- Vercel's own Git integration handles this natively — connect the repo, every PR
  gets a preview URL, merges to `main` deploy to prod. Minimal custom CI needed
  beyond lint/typecheck/test on PR.

**Mobile (`mobile/` or separate repo)**
- Lint + `flutter test` on PR. Build artifacts on tag push (§5) — hold off on full
  store-upload automation until there's a real release cadence.

### Artifact promotion between data engine and backend
This is the one genuinely cross-subsystem CI concern: how does a new model artifact
actually get from a data-engine training run onto the backend VM?
- Simplest version: the data-engine's scheduled workflow, after a successful
  versioned training run, copies the artifact + metadata to the VM's
  `/data/models/<version>/` directory (via `scp`/`rsync` in the workflow, using a
  deploy key scoped only to that path) and updates a `latest` symlink/pointer.
- The backend picks up the new artifact on its next restart (already how
  `lru_cache`-based loading works per the existing conventions) — so promotion is a
  **file copy + a deliberate restart**, not a live hot-swap. Keep it that way for now;
  a hot-reload mechanism is unnecessary complexity at this stage.
- Do **not** let the data-engine CI job restart the backend automatically on every
  artifact push — a bad artifact should require a human decision to roll forward,
  not an automatic one. Trigger the restart as a manual or separately-approved step.

---

## 8. Secrets management

- **GitHub Actions secrets** for CI-time credentials (deploy SSH key, container
  registry token, Africa's Talking sandbox vs. prod API keys — kept as distinctly
  named secrets, never one shared key reused across environments).
- **On the VM**: a single `.env` file per environment (`*.env.staging`,
  `*.env.production`), never committed, loaded by Docker Compose — `JWT_SECRET_KEY`,
  `DATABASE_URL` (remember: URL-encode any `@` in the password as `%40`, and escape
  `%` as `%%` for Alembic per the existing documented gotcha), SMS/USSD gateway keys,
  push notification service credentials.
- Rotate `JWT_SECRET_KEY` and gateway credentials on any suspected exposure — since
  this is a small team on a free-tier VM without a dedicated secrets manager, the
  realistic mitigation is discipline (never commit `.env`, restrict VM SSH access to
  the team) rather than infrastructure, but write that discipline down as a stated
  policy, not an assumption.

---

## 9. Monitoring, logging, and backups

Given free-tier resource constraints, favor lightweight external tools over
self-hosted observability stacks (a self-hosted Prometheus/Grafana stack would eat a
meaningful chunk of that 12GB budget for little benefit at this scale):

- **Uptime**: a free external uptime checker (UptimeRobot or similar) pinging
  `/health` — costs nothing to run, and it's the single fastest way to know the VM or
  app went down before a user reports it.
- **Error tracking**: Sentry's free tier, wired into the backend (and the
  reconciliation worker specifically, per the backend handoff's observability gap) —
  don't self-host an error tracker on the same constrained VM you're trying to
  monitor.
- **Structured logs**: JSON-formatted app logs to stdout, captured by Docker's
  logging driver, rotated (set `max-size`/`max-file` in the Compose file explicitly —
  unbounded local logs on a small block volume will eventually fill the disk, which
  is a realistic failure mode here, not a theoretical one).
- **Backups — this matters more than usual given the local-disk photo storage
  decision**:
  - Postgres: nightly `pg_dump` to the block volume, plus a periodic off-box copy
    (even just a scheduled push to a free-tier object storage bucket or a GitHub
    Actions job that pulls and archives it) — a single-VM setup with no off-box
    backup means a lost VM is a lost database, not just lost uptime.
  - Photos: since these live on local disk by design (per the mobile contract's
    decision), the same single-point-of-failure risk applies — a periodic sync of
    `/data/photos` to Oracle's free 10GB object storage tier (or wherever is
    cheapest) is worth setting up early rather than treating it as a someday task,
    precisely because it was already flagged as a known limitation when the local-disk
    decision was made.

---

## 10. Integration testing across subsystems

The staging environment (§2) is the actual integration point — the place all four
teams' work meets before it's real. Make it earn that role:
- **Mobile and USSD point at staging by config, not by hardcoding** — same
  environment-flavor mechanism as §5, so switching a build from staging to prod is a
  build flag, not a code change.
- **Contract stability matters more than usual here** because four different
  people/teams are building against the same API surface in parallel. Any breaking
  change to a `/mobile/*` or `/ml/*` response shape should be called out explicitly
  (a version bump note, a message to the other teams) — not just merged silently,
  since the mobile app and USSD flow can't see a Swagger diff the way a person can.
- **A lightweight end-to-end smoke test worth having early**: capture a shipment via
  the mobile app (or a script hitting `/mobile/shipments/sync` directly) against
  staging, confirm it reaches `shipment_sync_staging`, run the reconciliation
  service to promote it into `shipments`, and confirm
  `/mobile/shipments/{id}/recommendation` returns a sane result — this single flow
  touches data engine artifacts, backend logic, and the mobile contract all at once,
  so it's the highest-value one test to automate first if only one gets built.

  Note: the reconciliation service is not yet wired to a periodic scheduler. For
  the smoke test, call `run_reconciliation()` directly or trigger it via a
  management endpoint.

---

## 11. Release & rollback strategy

- **Backend**: tag-based releases, Docker image tagged with the git SHA (not just
  `latest`) so a rollback is "redeploy the previous SHA's image," not "hope the last
  build still exists somewhere."
- **Database migrations**: write every Alembic migration to be reversible where
  practical (a working `downgrade()`), and avoid combining a schema migration with a
  risky data backfill in the same deploy — split them so a bad backfill doesn't force
  a full schema rollback too.
- **Model artifacts**: versioned directories with a `latest` pointer (per §7) means
  rollback is repointing the symlink and restarting — keep at least the last 2–3
  versions on disk specifically so this is always possible without waiting on a
  re-train.
- **Frontend**: Vercel keeps prior deployments accessible by default — rollback is a
  dashboard click, effectively free to rely on.

---

## 12. AI context packet (for vibecoding DevOps/CI work)

```
PROJECT: Fresh Supplies infrastructure. Target hosting: single Oracle Cloud Always
Free Ampere A1 VM — CURRENTLY 2 OCPU / 12GB RAM (Oracle silently halved this from
4 OCPU/24GB in June 2026; always size new work for 2 OCPU/12GB and treat that number
as provisional, verify against current Oracle docs before assuming more capacity is
available). Frontend deploys separately on Vercel's free tier, not on the same VM.

Everything backend-side is Docker Compose based: backend (FastAPI/uvicorn), postgres,
a reconciliation worker, behind Caddy for reverse proxy + automatic TLS. Data engine
training does NOT run as a long-lived service on this VM — it's a scheduled batch job
(GitHub Actions or VM cron) that produces versioned artifacts and pushes them to
/data/models/<version>/ on the VM; the backend picks up a new version via a manual/
approved restart, not a live hot-swap.

DO NOT propose a Kubernetes-based deployment, a multi-node setup, or any
infrastructure that assumes more than ~2 OCPU/12GB of always-on compute — this is a
genuine hard constraint, not a starting point to scale up from casually. If a task
seems to need more than that, flag it as a capacity/cost decision rather than quietly
designing around an assumption of more resources.

Secrets: .env files per environment on the VM (never committed), GitHub Actions
secrets for CI-time credentials. Known DATABASE_URL gotchas: URL-encode a literal @ in
the password as %40; escape % as %% for Alembic's env.py interpolation.

Model artifact promotion and photo storage are both local-disk-based by deliberate
choice (not S3/object storage yet) — treat this as an intentional current-phase
decision with a documented backup mitigation (periodic sync to object storage), not
something to "fix" by silently introducing a cloud storage dependency without it being
raised as a change.

When proposing a CI/CD change, state which existing workflow/environment convention
you're extending, and flag explicitly if a proposed step would increase steady-state
resource usage on the always-on VM.

The mobile API namespace (/mobile/*) is fully implemented with 11 endpoints.
The reconciliation service exists but needs a scheduler (APScheduler, cron, or
a Celery/RQ worker). i18n is built (en/sw) in app/core/i18n.py. Photo storage
is local disk, no resize pipeline yet.
```

---

## 13. Suggested build order

1. Provision the Oracle VM at the correct (reduced) size, set up Caddy + domain +
   TLS, and get a bare `docker compose up` backend+Postgres stack running manually —
   prove the target environment works before automating deploys to it.
2. Backend CI: lint/test on PR, build+push image on merge, manual first deploy to
   confirm the pipeline before automating the deploy step itself.
3. Alembic migration step wired explicitly into the deploy pipeline (§7).
4. Frontend on Vercel — fastest win, mostly configuration not infrastructure.
5. Backup jobs (Postgres dump + photo sync) — do this **before** real user data
   accumulates, not after, given the single-VM/local-disk risk already accepted.
6. Staging environment + the one cross-subsystem smoke test (§10) — this is what
   actually protects the four teams building in parallel.
7. Data engine scheduled retrain + artifact promotion pipeline (§7).
8. Mobile CI builds + internal test track distribution (§5).
9. USSD sandbox integration (§6) — start the Africa's Talking account/shortcode
   process early given its likely lead time, even if the flow itself isn't ready.
10. i18n infrastructure (app/core/i18n.py) is built with en/sw translations — no
    backend work needed for locale support, just Accept-Language header handling.

---

## 14. Open questions to raise, not guess on

- Confirm current Oracle Always Free limits directly against Oracle's own docs at
  provisioning time — this document's numbers are accurate as of this writing but
  Oracle has already changed them once without notice this year.
- Monorepo vs. separate repos per subsystem — affects how the CI workflows above are
  actually laid out (path-filtered jobs in one repo vs. fully separate pipelines).
  Not specified by anything discussed so far; worth deciding before building the
  workflows themselves.
- Who owns the Africa's Talking account and billing once past sandbox — a team/
  process question, not a technical one, but worth settling before production USSD
  traffic depends on it.
