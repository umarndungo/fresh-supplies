"""Model regression tests.

These guard against the project's key ML anti-pattern: a spoilage target that is
a deterministic function of the training features, which produces a misleadingly
perfect AUC (~0.99) purely by inverting the label-generating formula.

If any of these fail after a change to the label generator or models, it means
the target has either (a) become circular again, or (b) the saved artifact is
stale / inconsistent with the training features.
"""

import joblib
import numpy as np
import pandas as pd

from src.crops import CROP_NAMES, SPOILAGE_FRAILTY
from src.predictive_models import PredictiveModels, _build_realistic_spoilage

FOOD_DIR = "data/processed/food"


def _sample_food_df(n=3000, seed=0):
    df = pd.read_csv(f"{FOOD_DIR}/integrated_post_harvest_food.csv")
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(df), size=min(n, len(df)), replace=False)
    return df.iloc[idx].reset_index(drop=True)


def test_model_artifact_loads_and_predicts_monotonically():
    """Cold/short routes should predict LOWER spoilage than hot/long routes."""
    bundle = joblib.load(f"{FOOD_DIR}/food_model_inference.joblib")
    clf, features = bundle["classifier"], bundle["feature_names"]

    base = {f: 0.0 for f in features}
    base.update({
        "Temperature_C": 22.0, "Pressure_PSI": 30.0, "Transit_Duration_Hr": 3.0,
        "baseline_loss_pct": 8.0, "Thermal_Heat_Exposure": 0.0,
        "Distance_To_Market_Km": 20.0, "price_per_kg": 60.0,
    })
    cold = pd.DataFrame([{**base}], columns=features)

    hot = pd.DataFrame([{**base, "Temperature_C": 38.0,
                         "Transit_Duration_Hr": 18.0,
                         "Thermal_Heat_Exposure": (38 - 25) * 18.0}],
                       columns=features)

    p_cold = clf.predict_proba(cold)[0][1]
    p_hot = clf.predict_proba(hot)[0][1]
    assert p_cold < p_hot, f"cold={p_cold:.3f} should be < hot={p_hot:.3f}"


def test_artifact_feature_set_matches_prepare_features():
    """The saved model's feature names must match the current training features,
    otherwise the API would silently feed mis-aligned columns."""
    from src.train_food_model import engineer_food_features

    bundle = joblib.load(f"{FOOD_DIR}/food_model_inference.joblib")
    df = engineer_food_features(pd.read_csv(f"{FOOD_DIR}/food_market_annotated.csv"))
    pm = PredictiveModels()
    pm.prepare_features(df)
    assert set(pm.feature_names) == set(bundle["feature_names"]), (
        set(pm.feature_names) ^ set(bundle["feature_names"])
    )


def test_label_generator_is_not_circular():
    """The spoilage target must NOT be a near-deterministic function of the
    features. A believable model has AUC well below ~0.99."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import train_test_split

    df = _build_realistic_spoilage(_sample_food_df())
    pm = PredictiveModels()
    X, y = pm.prepare_features(df)

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=0)
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, n_jobs=-1)
    clf.fit(Xtr, ytr)
    auc = roc_auc_score(yte, clf.predict_proba(Xte)[:, 1])
    # Real-world ceiling guard: not near-perfect (>=0.97) would imply the model
    # is inverting the label formula.
    assert auc < 0.97, f"AUC {auc:.3f} suspiciously high => circular target?"
    assert auc > 0.60, f"AUC {auc:.3f} too low => no learnable signal"


def test_crop_catalogue_consistent():
    """crops.yaml frailty keys must match the documented crop names."""
    assert set(SPOILAGE_FRAILTY) == set(CROP_NAMES)
    assert len(CROP_NAMES) >= 5
    assert all(v > 0 for v in SPOILAGE_FRAILTY.values())


def test_scored_dataset_has_all_crops():
    """The scored FOOD dataset should cover every catalogue crop."""
    scored = pd.read_csv(f"{FOOD_DIR}/food_scored.csv")
    present = set(scored["crop_type"].unique())
    assert present == set(CROP_NAMES), set(CROP_NAMES) - present
    assert {"spoilage_prob", "risk_tier"}.issubset(scored.columns)


def test_numpy_feature_magnitudes_finite():
    """Generated features + label must be finite and within expected range."""
    df = _build_realistic_spoilage(_sample_food_df())
    assert np.isfinite(df["estimated_loss_pct"]).all()
    assert df["estimated_loss_pct"].between(0, 60).all()
