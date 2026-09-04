# FreshRoute AI — Data Engine Developer Handoff

Purpose: what to build/improve next on `post_harvest_data_engine/`, why it matters
given where the rest of the system now is, and enough context to vibecode accurately
without reintroducing a bug that was already found and fixed once.

---

## 1. Project context (read first)

The data engine is in genuinely good shape — this is not a "fix it" handoff, it's a
"here's what's next now that the rest of the system is catching up" handoff. Recent
work already fixed the most important issue: the spoilage label used to be
predictable almost perfectly from the same features used to predict it (ROC-AUC
0.9957), because the synthetic target formula and the feature set overlapped too
closely. That's fixed — `_build_realistic_spoilage()` now injects irreducible noise
outside the feature space, AUC dropped to a defensible ~0.867, and a regression test
now fails the suite if AUC creeps back above 0.97. **Do not loosen or remove that
guard** — it exists specifically to prevent quietly reintroducing the original bug.

Two other things already landed: crop configuration is now a single source of truth
(`config/crops.yaml`, consumed by all four modules that used to require manual
syncing), and there's a documented "Known Limitations & Caveats" section covering
synthetic market prices, the thin FAOSTAT baseline, and no model versioning.

---

## 2. Deliverables — what's next

### 2.1 Real-data ingestion path from the mobile capture flow — the big opportunity
Once the backend's `shipment_sync_staging` → `shipments` reconciliation is live (see
the backend handoff), FreshRoute will start accumulating **real, field-captured
shipment data** for the first time — crop, quantity, GPS location, timestamp, and
(eventually) actual outcome if a "was this shipment actually spoiled on arrival"
field gets added to the driver confirmation flow. This is worth prioritizing highly:
- Build an export/ingestion script that pulls reconciled real shipments out of the
  backend DB into a format the data engine can consume alongside (not instead of) the
  synthetic telemetry.
- Even without a ground-truth "spoiled/not spoiled" outcome yet, real
  location/crop/timing data can validate whether the synthetic telemetry's
  distributions (temperature curves, transit durations, crop mix) actually resemble
  reality — a cheap, high-value sanity check before investing more in synthetic
  realism.
- If/when a real outcome field does get added on the backend side, this becomes the
  path to actually validating (or correcting) the model against ground truth instead
  of only against its own synthetic target — which is the single most important
  thing that would upgrade this from "well-engineered synthetic model" to "validated
  predictive model."

### 2.2 Model artifact versioning
Currently a `.joblib` file gets overwritten on retrain and picked up via `lru_cache`
on backend restart — no version history, no rollback, no record of what data/config
produced a given model. Minimum viable fix:
- Include a metadata sidecar with each artifact: training timestamp, git commit hash,
  feature list, crop list version (from `crops.yaml`), and the validation AUC.
- Keep the last N artifact versions on disk (or in whatever storage the backend team
  lands on for photos — worth checking if that infra can be shared) rather than
  overwriting in place, so a bad retrain can be rolled back without redoing the run.
- This doesn't need to be elaborate (no need for a full MLflow-style registry) — a
  timestamped directory per training run plus a `latest` pointer is enough for now.

### 2.3 Market price realism
Prices are still fully synthetic (`CROP_BASE_PRICE_KES` + `REGION_VARIATION`
multipliers). This is already documented as a limitation, which is the right stance
for now — but if there's room this cycle, even a partial real-price ingestion (e.g.
scraping Kenya's Ministry of Agriculture or RATIN market bulletins for a subset of
the 9 supported crops) would materially strengthen the "revenue retained" ranking,
which is the actual product value proposition. Treat this as a stretch goal, not a
blocker — don't let it compete with §2.1 for priority.

### 2.4 Extend the regression test suite
19 tests total right now, concentrated on the label-circularity guard and the `/ml`
contract. Worth adding:
- A test asserting `food_scored.csv` and `market_prices.csv` continue to cover the
  same crop set after any `crops.yaml` change (this coupling is currently a
  documented convention, not an enforced one).
- A test on `recommend_market_for_shipment()`'s revenue-retained ranking logic in
  isolation, independent of the full model pipeline.

### 2.5 Observability on pipeline runs
No structured logging currently on `main.py` / `train_food_model.py` runs beyond
print statements. Doesn't need to be elaborate — enough to answer "did last night's
retrain succeed, and what were the headline metrics" without re-reading stdout.

---

## 3. Explicitly out of scope this phase

- Nothing about the backend or frontend — you're not touching FastAPI routes or
  Next.js components. If a request from those teams implies a data engine change,
  it should come through as a defined ask (new feature, new crop, new artifact
  shape), not an assumption you fill in.
- A full model registry (MLflow, etc.) — §2.2's lightweight versioning is the actual
  ask; don't over-build this.
- Live market price API integration — still no public API exists for these
  horticulture crops; §2.3 is a manual/scraped stopgap at most, not a real-time feed.

---

## 4. AI context packet (for vibecoding)

```
PROJECT: FreshRoute AI data engine — post_harvest_data_engine/, Python ETL + ML
training. Pipeline: main.py drives ingestion (src/ingestion.py, FAOSTAT + synthetic
telemetry) -> grouping (src/grouping.py, splits by food_class) -> market pricing
(src/market_pricing.py) -> model training (src/train_food_model.py,
src/predictive_models.py) -> Streamlit dashboards for review.

CRITICAL — DO NOT reintroduce label circularity. The spoilage target in
_build_realistic_spoilage() (predictive_models.py) must retain noise/variance that is
NOT fully derivable from the model's own feature set. A regression test fails the
suite if validation ROC-AUC exceeds ~0.97 on the food model — this is intentional and
protects against a real bug that was already found and fixed once (the model was
previously reconstructing its own synthetic label formula, producing a meaningless
0.9957 AUC). If a change increases AUC substantially, treat that as a signal to
investigate for a new leak, not as an improvement to celebrate.

Crop configuration lives in config/crops.yaml as the single source of truth, consumed
by telemetry_generator, ingestion, market_pricing, and predictive_models. Do not
hardcode a crop list in any new module — read from this file. Adding a new crop means
updating crops.yaml only, then regenerating (delete stale raw_telemetry.csv first) and
retraining.

Known, already-documented limitations (do not silently "fix" by pretending the data is
more real than it is): market prices are synthetic-but-calibrated; the FAOSTAT Kenya
baseline is 300 records/108 crops for a single country-year, useful as context, not
a strong statistical foundation; there is no model registry (see §2.2 as the actual
fix in progress).

FAOSTAT ingestion is offline/deterministic from local CSVs — no live API calls. Do
not add a live network dependency into src/faostat_downloader.py without flagging it
first, since the system's determinism (same input CSVs -> same output every run) is a
deliberately relied-upon property elsewhere (tests, dashboards).

When touching predictive_models.py or train_food_model.py, run the existing model
regression test before and after your change and report both AUC values — don't just
report "tests pass," report the actual number, since a passing-but-degraded AUC (e.g.
still under the 0.97 ceiling but meaningfully lower than baseline for no clear reason)
is itself worth flagging.
```

---

## 5. Suggested build order

1. Model artifact versioning (§2.2) — small, self-contained, de-risks everything else
   you touch this cycle (you can always roll back).
2. Real-data ingestion script from reconciled shipments (§2.1) — coordinate timing
   with the backend developer; no point building this before staging/reconciliation
   exists on their end, but the script itself can be written and tested against a
   mocked export in parallel.
3. Regression test extensions (§2.4).
4. Observability (§2.5).
5. Market price realism (§2.3) — stretch, lowest priority, do only if time allows.

---

## 6. Open questions to raise, not guess on

- Will the driver confirmation flow ever capture an actual "was this shipment
  spoiled on arrival" outcome? This determines whether §2.1's real-data path is
  "richer synthetic-realism validation" (useful now) or "actual ground-truth model
  validation" (transformative later) — worth raising with the backend/product owner
  rather than assuming either way.
- Where should versioned model artifacts physically live — same local-disk approach
  the backend is using for photos (Oracle Free Tier), or elsewhere? Worth checking
  before building §2.2 so the two efforts don't diverge on storage approach
  unnecessarily.
