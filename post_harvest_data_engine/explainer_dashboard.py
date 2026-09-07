"""
Fresh Supplies — ML Explainer Dashboard.

A simple educational Streamlit app that walks through, end to end:
  1. Where our data comes from
  2. The ETL pipeline (ingestion -> cleaning -> feature engineering)
  3. How the ML model is trained (imbalance handling)
  4. The results: predictions, feature importance, SHAP, risk tiers
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns

sys.path.insert(0, os.path.dirname(__file__))
from src.predictive_models import PredictiveModels, _build_realistic_spoilage
from src.feature_engineering import engineer_pipeline_features
from config import settings  # noqa: F401  (imported for visibility)

st.set_page_config(
    page_title="Fresh Supplies — ML Explainer",
    page_icon="🌾",
    layout="wide",
)

PROCESSED_CSV = "data/processed/integrated_post_harvest_dataset.csv"


# ---------------------------------------------------------------------------
# Caching the heavy compute once so the app is responsive.
# ---------------------------------------------------------------------------
@st.cache_data
def load_training_artifacts():
    """Run the full spoilage pipeline and return everything the UI needs."""
    df = pd.read_csv(PROCESSED_CSV)
    df = _build_realistic_spoilage(df)  # feature engineer thermal load + target

    pm = PredictiveModels()
    X, y = pm.prepare_features(df)
    pm.train_and_evaluate(X, y)

    importances, indices = pm.get_feature_importance()
    feature_importance = pd.DataFrame(
        {"feature": [pm.feature_names[i] for i in indices],
         "importance": importances[indices]}
    )
    df["risk_tier"] = pm.segment_risk(X)
    df["spoilage_prob"] = pm.best_pipeline.predict_proba(X)[:, 1]
    return df, pm, X, y, feature_importance


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
st.markdown("## 🌾 Fresh Supplies — How Our Data & Model Work")
st.caption("A simple visual walkthrough of the spoilage-prediction pipeline — from raw data to ML results.")

tab = st.sidebar.radio(
    "Pipeline step",
    [
        "1 · Data Sources",
        "2 · ETL & Cleaning",
        "3 · Feature Engineering",
        "4 · The Model",
        "5 · Results & Insights",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Fresh Supplies** · Post-harvest spoilage prediction")

# ---------------------------------------------------------------------------
# 1. DATA SOURCES
# ---------------------------------------------------------------------------
if tab == "1 · Data Sources":
    st.header("1 · Where our data comes from")
    st.markdown(
        "We combine **four** data sources into a single integrated view. "
        "Each contributes a different piece of the spoilage puzzle."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🌍 Agricultural Production  (FAOSTAT)")
        st.markdown(
            "Local FAO CSV files give us **crop baselines**: which crops are grown, "
            "production volume, yield, and area harvested (Kenya, 2024)."
        )
        paths = [
            "data/raw/FAOSTAT_data_en_8-19-2026.csv",
            "data/raw/Production_Crops_Livestock_E_Africa.csv",
        ]
        for p in paths:
            if os.path.exists(p):
                st.markdown(f"✅ `{p}`")
            else:
                st.markdown(f"⚠️ `{p}` (not found)")
    with c2:
        st.subheader("🌡️ Weather  (CHIRTS / CHIRPS)")
        st.markdown(
            "Climate rasters sampled at each GPS coordinate give the **thermal stress** "
            "(hot-day frequency >34°C) — a primary driver of produce deterioration."
        )
        st.subheader("🚚 Logistics Telemetry  (synthetic)")
        st.markdown(
            "Sensor logs: temperature, pressure, GPS, shift. Generated with "
            "`telemetry_generator.py` (10,000 rows)."
        )
        st.subheader("💰 Market Pricing  (synthetic)")
        st.markdown("Price per crop per market — used later for revenue-retention routing.")

    if os.path.exists(PROCESSED_CSV):
        st.markdown("### The integrated dataset (after fusion)")
        df_preview = pd.read_csv(PROCESSED_CSV)
        st.dataframe(df_preview.head(10), use_container_width=True)
        st.caption(f"Full dataset: {df_preview.shape[0]:,} rows")
    else:
        st.warning("Integrated dataset not found — run the ingestion pipeline first.")

# ---------------------------------------------------------------------------
# 2. ETL & CLEANING
# ---------------------------------------------------------------------------
elif tab == "2 · ETL & Cleaning":
    st.header("2 · The ETL pipeline & data cleaning")
    st.markdown(
        "**E**xtract → **T**ransform → **L**oad. Raw files are parsed, cleaned, "
        "and merged into one table by `src/ingestion.py`."
    )

    import importlib
    import src.ingestion as ing
    importlib.reload(ing)

    st.subheader("Step-by-step")
    steps = [
        ("1. Extract", "Read raw FAOSTAT CSVs + telemetry + climate rasters."),
        ("2. Clean", "Clamp out-of-range values (temperature ±50°C, valid pressure) and drop bad rows."),
        ("3. Merge", "Join crop baselines with telemetry on crop/zone → one row per sensor record."),
        ("4. Location", "Derive a readable `location` string from lat/lon coordinates."),
        ("5. Load", "Write `data/processed/integrated_post_harvest_dataset.csv`."),
    ]
    for title, desc in steps:
        st.markdown(f"**{title}** — {desc}")

    if os.path.exists(PROCESSED_CSV):
        df = pd.read_csv(PROCESSED_CSV)
        st.subheader("Cleaned dataset overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", f"{df.shape[0]:,}")
        c2.metric("Columns", df.shape[1])
        c3.metric("Nulls (total)", int(df.isna().sum().sum()))

        st.markdown("**Column types after cleaning**")
        ct = df.dtypes.astype(str).reset_index()
        ct.columns = ["column", "dtype"]
        st.dataframe(ct, use_container_width=True)

        st.markdown("**Missing values per column**")
        miss = df.isna().sum()
        if miss.sum() == 0:
            st.success("No missing values — clean dataset. ✅")
        else:
            st.dataframe(miss[miss > 0].reset_index().rename(
                columns={"index": "column", 0: "nulls"}), use_container_width=True)

# ---------------------------------------------------------------------------
# 3. FEATURE ENGINEERING
# ---------------------------------------------------------------------------
elif tab == "3 · Feature Engineering":
    st.header("3 · Feature Engineering")
    st.markdown(
        "Raw columns alone aren't enough. We derive **predictive features** "
        "that capture *how* spoilage actually happens."
    )

    with st.expander("How we build features", expanded=True):
        st.markdown(
            """
- **`Temperature_C`** — instantaneous sensor temperature.
- **`Transit_Duration_Hr`** — how long the produce has been in transit.
- **`Thermal_Heat_Exposure` = max(0, Temp−25°C) × Transit_Hours** — the
  *cumulative* heat load (degree-hours). This is the feature our model found
  most important: it's not just how hot it is, but **how hot × how long**.
- **`baseline_loss_pct`** — the crop's expected loss floor.
- **Zone / Shift** — categorical context one-hot encoded.
            """
        )

    df = pd.read_csv(PROCESSED_CSV)
    engineered = _build_realistic_spoilage(df.copy())
    eng_cols = ["Temperature_C", "Transit_Duration_Hr", "Thermal_Heat_Exposure"]
    if all(c in engineered.columns for c in eng_cols):
        st.subheader("Thermal load vs. spoilage — the core idea")
        fig, ax = plt.subplots(figsize=(9, 4))
        sns.scatterplot(
            data=engineered.sample(min(2000, len(engineered)), random_state=1),
            x="Thermal_Heat_Exposure",
            y="estimated_loss_pct",
            hue="crop_type",
            alpha=0.5,
            ax=ax,
        )
        ax.set_title("Higher cumulative heat exposure → higher estimated spoilage %")
        ax.set_xlabel("Thermal Heat Exposure (degree-hours)")
        ax.set_ylabel("Estimated Loss (%)")
        st.pyplot(fig)

        st.subheader("Sample of engineered rows")
        st.dataframe(engineered[eng_cols + ["crop_type", "estimated_loss_pct"]].head(20),
                     use_container_width=True)

# ---------------------------------------------------------------------------
# 4. THE MODEL
# ---------------------------------------------------------------------------
elif tab == "4 · The Model":
    st.header("4 · The ML model")
    with st.spinner("Training models (RF + XGBoost, 5-fold CV)…"):
        df, pm, X, y, importance = load_training_artifacts()

    st.markdown(
        "We adapted **Week 9's operational ML playbook** to spoilage prediction: "
        "classify each shipment as **spoiled (loss >15%)** vs. not, using two "
        "tree-based models compared under **stratified 5-fold cross-validation**."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Class imbalance handling**")
        pos = int(y.sum())
        neg = int(len(y) - pos)
        st.progress(pos / len(y))
        st.markdown(
            f"- Spoiled (positive): **{pos:,}** ({pos/len(y)*100:.1f}%)\n"
            f"- Fresh (negative): **{neg:,}** ({neg/len(y)*100:.1f}%)"
        )
        st.caption(
            "The positive class is the minority, so we use **SMOTE inside the "
            "pipeline** (per-fold, leak-free) + class weighting."
        )
    with c2:
        st.markdown("**Cross-validation results**")
        rows = []
        for name, aucs in pm.cv_results.items():
            rows.append({"Model": name.upper(), "ROC-AUC (mean)": f"{aucs.mean():.4f}",
                         "ROC-AUC (±std)": f"{aucs.std():.4f}"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        st.caption(f"Best model: **{pm.best_model_name.upper()}**")

    st.markdown("---")
    st.subheader("What's in the box")
    if pm.best_model_name == "rf":
        desc = "**Random Forest** — an ensemble of decision trees averaging their votes for robust, non-linear classification."
    else:
        desc = "**XGBoost** — gradient-boosted trees that iteratively correct errors; excellent on tabular data."
    st.markdown(desc)

# ---------------------------------------------------------------------------
# 5. RESULTS & INSIGHTS
# ---------------------------------------------------------------------------
elif tab == "5 · Results & Insights":
    st.header("5 · Results & insights")
    with st.spinner("Loading trained model…"):
        df, pm, X, y, importance = load_training_artifacts()

    st.markdown("### What the model learned")
    st.markdown(
        "The single biggest driver of predicted spoilage is **`Thermal_Heat_Exposure`** — "
        "the cumulative degree-hours in transit, far above raw temperature. "
        "This tells us a **longer but cooler route can beat a shorter hot one**."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Feature importance")
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.barplot(data=importance, x="importance", y="feature", palette="viridis", ax=ax)
        ax.set_title("Global feature importance")
        ax.set_xlabel("Importance")
        st.pyplot(fig)
    with c2:
        st.subheader("Risk tiers (K-Means)")
        tiers = df["risk_tier"].value_counts().sort_index()
        tier_names = {0: "Fresh", 1: "At-Risk", 2: "Critical"}
        rename = {k: tier_names.get(k, k) for k in tiers.index}
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.pie(tiers.values, labels=[rename[k] for k in tiers.index],
               autopct="%1.1f%%", startangle=90, colors=["#2ecc71", "#f1c40f", "#e74c3c"])
        ax.set_title("Segmentation of shipments")
        st.pyplot(fig)

    st.subheader("Sample predictions")
    show = df[["crop_type", "Temperature_C", "Thermal_Heat_Exposure",
               "estimated_loss_pct", "spoilage_prob", "risk_tier"]].copy()
    show["risk_tier"] = show["risk_tier"].map(tier_names)
    show["spoilage_prob"] = show["spoilage_prob"].round(3)
    st.dataframe(show.head(20), use_container_width=True)

    st.info(
        f"**Bottom line:** XGBoost reached **{pm.cv_results['xgb'].mean():.2f} ROC-AUC**, "
        f"and predicts spoilage primarily from **cumulative thermal load**. "
        "Next, this probability feeds the route optimizer to pick cooler, faster, "
        "more profitable markets."
    )
