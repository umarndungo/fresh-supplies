# Multi-tenancy design

Status: **draft for review — no code changes yet.** This supersedes the interim
scoping shipped earlier today (`_CROSS_TENANT_ROLES` in `shipment_service.py` /
`produce_service.py`), which was a stopgap pending this design.

## 1. Tenant model

A **tenant** is either:
- a **cooperative** (`cooperatives` row) — one or more `FARMER_COOPERATIVE`
  members share one pool of shipments/produce, or
- a **solo farmer** — a `FARMER_COOPERATIVE` account with no `cooperative_id`
  set, who is their own tenant (self-service, no sharing).

This is exactly the `OwnerType.COOPERATIVE` / `OwnerType.INDIVIDUAL` split that
already exists and is already used by the mobile shipment path
(`mobile_shipment_service.py`) — the fix here is making the **web** path and
**produce** use the same model consistently, instead of two different partial
implementations.

Every shipment/produce record's tenant is `(owner_type, cooperative_id |
created_by)`:
- `owner_type = COOPERATIVE` → tenant is `cooperative_id` (real FK to
  `cooperatives.id`).
- `owner_type = INDIVIDUAL` → tenant is the creator (`created_by`); no
  `cooperative_id`.

Three account tiers now exist for people, not one:
1. **Platform staff with a home tenant** — `LOGISTICS_MANAGER` / `MARKET_ANALYST`
   see *only* cooperatives explicitly granted to them (see §4). Zero grants =
   zero visible data, not everything.
2. **`ADMINISTRATOR` ("super admin") — platform/billing role, NEVER a data
   role.** **Revised per your last message:** `ADMINISTRATOR` can create and
   manage tenants (cooperatives) and see aggregate usage for billing, but is
   now explicitly **forbidden from ever reading shipment/produce row content**
   for any tenant — not "can see everything," the opposite. This is a hard
   rule enforced in code (§4, §7), not just a UI restriction: the API itself
   returns nothing for `ADMINISTRATOR` on `/shipments` and `/produce`. What
   `ADMINISTRATOR` keeps: `/admin/users` (unchanged — account/role
   management is platform administration, not "tenant's internal data"),
   plus the new tenant-lifecycle and billing-usage endpoints in §7.
3. **`FARMER_COOPERATIVE`** — scoped to their own tenant (their cooperative's
   shared pool, or just their own records if solo). Within a cooperative, a
   new **`cooperative_role`** (`MEMBER` / `ADMIN`) distinguishes:
   - `MEMBER`: sees the whole cooperative's shipments/produce, but can only
     **mutate** (update/delete) what they personally created.
   - `ADMIN`: sees and can **mutate anything** in their cooperative, plus
     manages membership (§5). Whoever creates a cooperative becomes its first
     `ADMIN` on backfill/going forward.

## 2. Schema changes

### 2.1 `produce` — fix the mislabeled `cooperative_id`, add `owner_type` + `created_by`

Today: `cooperative_id: UUID NOT NULL, FK -> users.id`, actually holding the
*creator's own id* (see `produce_service.create_produce`: `cooperative_id=actor.id`).
No `created_by` column exists at all — there's currently no way to know *who*
within a shared pool logged an item, only who "owns" it (conflated).

**Migration `add_tenant_fields_to_produce`:**
```sql
ALTER TABLE produce ADD COLUMN owner_type owner_type_enum;
ALTER TABLE produce ADD COLUMN created_by UUID REFERENCES users(id);

-- Backfill from the existing (mislabeled) cooperative_id, which today IS the creator id:
UPDATE produce SET created_by = cooperative_id;

UPDATE produce p
SET owner_type = COALESCE(u.account_type, 'INDIVIDUAL')
FROM users u WHERE u.id = p.created_by;

-- Re-point cooperative_id at the creator's actual cooperative (or NULL if solo/individual):
UPDATE produce p
SET cooperative_id = u.cooperative_id
FROM users u
WHERE u.id = p.created_by AND p.owner_type = 'COOPERATIVE' AND u.cooperative_id IS NOT NULL;

UPDATE produce SET cooperative_id = NULL
WHERE owner_type = 'INDIVIDUAL' OR cooperative_id NOT IN (SELECT id FROM cooperatives);
-- ^ defensive: a COOPERATIVE-type creator whose own cooperative_id is somehow
-- NULL degrades to being scoped as an individual (owner_type forced INDIVIDUAL
-- too), rather than left dangling. Handled in a follow-up UPDATE:
UPDATE produce SET owner_type = 'INDIVIDUAL' WHERE owner_type = 'COOPERATIVE' AND cooperative_id IS NULL;

ALTER TABLE produce DROP CONSTRAINT produce_cooperative_id_fkey;
ALTER TABLE produce ADD CONSTRAINT produce_cooperative_id_fkey
    FOREIGN KEY (cooperative_id) REFERENCES cooperatives(id);
ALTER TABLE produce ALTER COLUMN cooperative_id DROP NOT NULL;
ALTER TABLE produce ALTER COLUMN owner_type SET NOT NULL;
ALTER TABLE produce ALTER COLUMN created_by SET NOT NULL;
```
Reuses the existing `owner_type_enum` (already created for `users`/`shipments`).

### 2.2 `shipments` — start actually setting `owner_type`

The column already exists (nullable) but the web create path never sets it —
only the mobile path does. No migration needed, just application-code
discipline: `ShipmentService.create_shipment` sets
`owner_type = actor.account_type or OwnerType.INDIVIDUAL` alongside the
`cooperative_id = actor.cooperative_id` fix already shipped. Existing NULL
rows are treated as `INDIVIDUAL` at query time (no backfill needed since the
scoping code treats `owner_type IS NULL` the same as `INDIVIDUAL`).

### 2.3 `users` — add `cooperative_role`

**Migration `add_cooperative_role_to_users`:**
```sql
CREATE TYPE cooperative_role_enum AS ENUM ('MEMBER', 'ADMIN');
ALTER TABLE users ADD COLUMN cooperative_role cooperative_role_enum;

-- Whoever created a cooperative is its admin:
UPDATE users u SET cooperative_role = 'ADMIN'
FROM cooperatives c WHERE c.created_by = u.id;

-- Everyone else already in a cooperative defaults to MEMBER:
UPDATE users SET cooperative_role = 'MEMBER'
WHERE cooperative_id IS NOT NULL AND cooperative_role IS NULL;
```
`NULL` for anyone without a `cooperative_id` (solo farmers, staff, admin) —
meaningless outside a cooperative context.

### 2.4 New table — `cooperative_access_grants`

**Migration `create_cooperative_access_grants`:**
```sql
CREATE TABLE cooperative_access_grants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cooperative_id UUID NOT NULL REFERENCES cooperatives(id) ON DELETE CASCADE,
    granted_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, cooperative_id)
);
CREATE INDEX ix_cooperative_access_grants_user_id ON cooperative_access_grants(user_id);
```
One row = "this `LOGISTICS_MANAGER`/`MARKET_ANALYST` can see this cooperative."
A user can hold many grants (many cooperatives); a cooperative can have many
grantees. **Decision I'm making explicit here:** only `ADMINISTRATOR` can
create/revoke grants (`POST/DELETE /admin/grants`) — a cooperative's own
`ADMIN` member cannot grant platform staff access to their data. Flag if you
want cooperative admins to have that power too; it's a small extension.

## 3. Domain layer changes

- `Shipment` (already patched today) — no further change.
- `ProduceItem` — add `owner_type: OwnerType`, `created_by: UUID`;
  `cooperative_id` becomes `UUID | None`.
- `User` — add `cooperative_role: CooperativeRole | None`.
- New `CooperativeRole(str, Enum)`: `MEMBER`, `ADMIN`.
- New `CooperativeAccessGrant` entity + `CooperativeAccessGrantRepository`
  (list grants for a user, create, delete).

## 4. Scoping algorithm

Computed once per request as a `VisibilityScope`, then applied identically to
shipments and produce:

```python
@dataclass(frozen=True)
class VisibilityScope:
    cooperative_ids: frozenset[UUID] = frozenset()   # visible cooperative tenants
    own_user_id: UUID | None = None      # visible "solo" tenant (individual)
    # No "unrestricted" flag anymore — nobody bypasses tenant scoping for
    # row-level content. ADMINISTRATOR is not in this function at all: the
    # service layer refuses ADMINISTRATOR before scope_for is even called
    # (see §7) — its absence here is deliberate, not an oversight.

def scope_for(actor: User, grants: CooperativeAccessGrantRepository) -> VisibilityScope:
    if actor.role in (UserRole.LOGISTICS_MANAGER, UserRole.MARKET_ANALYST):
        granted = grants.list_cooperative_ids_for(actor.id)
        return VisibilityScope(cooperative_ids=frozenset(granted))  # empty = sees nothing

    # FARMER_COOPERATIVE
    if actor.cooperative_id is not None:
        return VisibilityScope(cooperative_ids=frozenset({actor.cooperative_id}))
    return VisibilityScope(own_user_id=actor.id)
```

**Read** (`list_all`, `get_by_id`) — a record is visible iff:
```
(record.owner_type == COOPERATIVE and record.cooperative_id in scope.cooperative_ids)
or (record.owner_type == INDIVIDUAL and record.created_by == scope.own_user_id)
```
No admin bypass term here at all, per the revised rule.

**Mutate** (`update`, `delete`) — additionally:
```
(actor.role == FARMER_COOPERATIVE and actor.cooperative_role == ADMIN
    and record tenant == actor's cooperative)
or record.created_by == actor.id       # anyone can always edit their own record
or (actor.role == LOGISTICS_MANAGER and record tenant in actor's granted cooperatives)
    # ^ decided below, not left open — see §6.2
```
`ADMINISTRATOR` is absent from mutate too — it can't edit shipment/produce
content any more than it can read it. `MARKET_ANALYST` stays read-only
(it's an analytics role; nothing suggests it should ever write shipment/
produce data).

**Decision made, not left open:** `LOGISTICS_MANAGER` keeps mutate rights
(status updates, rerouting) but now scoped to *granted* cooperatives instead
of unscoped — this preserves today's real operational capability (dispatchers
need to update shipments) while still closing the tenancy hole. This resolves
what was previously flagged as open decision §6.2 in the prior draft.

## 5. New capability this unlocks: cooperative membership management

This was flagged as an open gap in the original implementation plan and
deferred. This design's `cooperative_role` makes it buildable:
- `POST /cooperatives/{id}/members` — invite/add a farmer (ADMIN of that
  cooperative, or platform ADMINISTRATOR, only).
- `DELETE /cooperatives/{id}/members/{user_id}` — remove a member (same
  permission), which also strips their access to that cooperative's shared
  data on their next request (their `cooperative_id` is cleared → they fall
  back to being a solo tenant of their own historical records).
- Not building this today unless you want it in this same pass — flagging
  because the schema now supports it and it directly closes a previously
  "explicitly deferred" gap.

## 6. Explicit decisions I made that need a yes/no, not just a read-through

1. Grants (`cooperative_access_grants`) are creatable **only by `ADMINISTRATOR`**,
   not by a cooperative's own `ADMIN` member. (§2.4) Consistent with
   `ADMINISTRATOR` being the sole platform-lifecycle role now — it can grant
   *other* staff visibility into a tenant without ever holding that
   visibility itself.
2. ~~`LOGISTICS_MANAGER` mutate scope~~ — resolved in §4: keeps mutate rights,
   scoped to granted cooperatives instead of unscoped.
3. A staff account (`LOGISTICS_MANAGER`/`MARKET_ANALYST`) with **zero grants**
   sees an empty list, not an error and not everything. The Analytics/Routes
   dashboards will render as empty for such an account until an admin grants
   them at least one cooperative — worth a "no cooperatives assigned yet"
   empty state in the frontend, not just a blank chart.
4. A `COOPERATIVE`-type user whose own `cooperative_id` is unexpectedly NULL
   (a data-integrity edge case, shouldn't happen but the migration guards it)
   is treated as `INDIVIDUAL` rather than erroring — silently degrades to
   "solo tenant of their own records" instead of failing closed. Alternative
   would be to fail closed (see nothing) — I'd rather this stay a visible,
   loud data-integrity bug (`is not None` assertion in a startup check) than
   silently reassign tenancy. Open to either.

## 7. Super admin: tenant creation + billing/usage (new, per your last message)

Two new, disjoint capability groups on `ADMINISTRATOR`, both explicitly
**metadata/aggregate only** — neither ever touches a `shipments`/`produce`
row:

### 9.1 Tenant lifecycle
- `POST /admin/tenants` — creates a `cooperatives` row (`name`) on behalf of
  a customer, e.g. during a sales/onboarding process before any farmer has
  signed up. Returns the new `cooperative_id`.
- `GET /admin/tenants` — list cooperatives (id, name, created_at, member
  count — a count, not the members' data) plus solo/individual tenants
  (derived: distinct `created_by`/`account_type=INDIVIDUAL` users with no
  `cooperative_id`).
- `PATCH /admin/tenants/{id}` — rename, deactivate a cooperative, etc.
- This does **not** replace self-service onboarding — a farmer can still
  create their own cooperative during mobile `complete-profile`
  (`mobile_auth_service.py`). This is an *additional* admin-initiated path,
  for the case where the platform sets up a tenant ahead of the farmer.
- Attaching members to an admin-created tenant reuses what already exists:
  `AdminCreateUserRequest`/`AdminUpdateUserRequest` already let
  `ADMINISTRATOR` set a user's `cooperative_id` via `/admin/users` — no new
  endpoint needed there, just confirming that field is respected (worth a
  quick check when this is implemented, not assumed).

### 9.2 Billing/usage — aggregate counts only, never row content
- `GET /admin/tenants/{id}/usage` returns e.g.:
  ```json
  {
    "cooperativeId": "...",
    "memberCount": 12,
    "shipmentCount": 340,
    "shipmentCountThisMonth": 28,
    "produceItemCount": 96,
    "totalQuantityKgThisMonth": 41200.0,
    "photoStorageBytesUsed": 118392044
  }
  ```
  Every field here is a `COUNT(*)`/`SUM(...)` SQL aggregate scoped to that
  tenant — the query never selects `origin`, `destination`, `crop`,
  coordinates, or any other business-content column, by construction (the
  repository method for this literally cannot return a row, only scalars).
  This is the structural guarantee behind "sees usage, not internal data":
  it's not a filtered version of the same query the tenant uses, it's a
  categorically different query shape.
- `GET /admin/tenants/usage` (plural) — the same, across all tenants, for a
  billing dashboard/export.

### 9.3 Enforcing "never," not just "by default"
Two places this has to be structural, not incidental, or a future refactor
could quietly reopen it:
1. `ShipmentService`/`ProduceService`'s `list_*`/`get_*`/mutate methods
   raise `ForbiddenError` immediately if `actor.role == UserRole.ADMINISTRATOR`
   — before `scope_for` even runs. `scope_for` (§4) doesn't handle
   `ADMINISTRATOR` at all, so this can't silently fall through to "sees
   everything" if someone edits the scope function later without noticing.
2. `CooperativeAccessGrantRepository.create()` validates the grantee's role
   is `LOGISTICS_MANAGER` or `MARKET_ANALYST` and rejects (`ValidationError`)
   an attempt to grant `ADMINISTRATOR` a cooperative — so "just grant the
   admin access" can't become a backdoor around rule §1.2.

## 8. Explicitly out of scope for this pass

- Region-based grants (`Cooperative` has no `region` field; would need one
  plus a way to grant-by-region instead of grant-by-cooperative-id).
- Any UI for managing grants or cooperative membership (API only).
- Nested/hierarchical cooperatives (federations of cooperatives).
- Migrating existing production data — this is written against a dev/staging
  DB; a real production cutover would need a maintenance-window runbook, not
  just the migration file.

## 9. Rollout order

1. Migrations 2.1–2.4 (can ship independently, in this order — 2.1 and 2.3 are
   backfills with no reader changes yet, so safe to land ahead of the
   scoping-code change; 2.4 is a pure additive table).
2. Domain/entity + repository changes (§3).
3. Scoping algorithm (§4) replacing today's interim `_CROSS_TENANT_ROLES` sets
   in `shipment_service.py` / `produce_service.py`.
4. Regression tests: extend `test_tenancy.py` with cooperative-sharing cases
   (two members of the same coop see each other's records; a granted analyst
   sees exactly their granted cooperatives and nothing else; an ungranted
   analyst sees nothing; a cooperative `ADMIN` can edit a member's record, a
   plain `MEMBER` cannot) **plus** the new negative cases from §7.3:
   `ADMINISTRATOR` gets `ForbiddenError` on every shipment/produce
   list/get/update/delete, and `CooperativeAccessGrantRepository.create()`
   rejects a grant targeting an `ADMINISTRATOR` user.
5. §7 tenant-lifecycle + billing/usage endpoints (`/admin/tenants*`) — new
   `AdminTenantService`, aggregate-only repository methods.
6. (Optional, same pass or fast-follow) §5 membership-management endpoints.
