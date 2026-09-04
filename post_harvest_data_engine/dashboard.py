"""
Streamlit Dashboard for Post-Harvest Loss & Crop Yield Intelligence.
Integrates local FAOSTAT CSV source files, telemetry, and climate analytics.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.ingestion import ingest_all_raw_files, merge_all_sources
from src.faostat_downloader import get_faostat_baseline_for_country
from src.grouping import load_grouped_dataset, PROCESSED_DIR, _group_dir

st.set_page_config(
    page_title="Fresh Supplies - Post-Harvest & Climate Engine",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Fresh Supplies: Post-Harvest Intelligence & Climate Engine")
st.markdown("Comprehensive dashboard parsing local FAOSTAT CSV source files, telemetry, and location analytics.")

FOOD_CLASS_GROUPS = ["FOOD", "FOOD_GRADE_OIL", "NON_EDIBLE"]

@st.cache_data
def load_pipeline_data(food_class: str = "FOOD"):
    try:
        all_raw = ingest_all_raw_files()
        baseline_file = _group_dir(food_class) / f"faostat_{food_class.lower()}.csv"
        baseline_df = pd.read_csv(baseline_file) if baseline_file.exists() else pd.DataFrame()

        from pathlib import Path
        merged_file = _group_dir(food_class) / f"integrated_post_harvest_{food_class.lower()}.csv"
        if merged_file.exists():
            merged_df = pd.read_csv(merged_file)
        else:
            merged_df = merge_all_sources()
        return all_raw, baseline_df, merged_df
    except Exception as e:
        st.error(f"Error loading ingestion pipeline: {e}")
        return {}, pd.DataFrame(), pd.DataFrame()

st.sidebar.header("Navigation & Filters")
app_mode = st.sidebar.selectbox("Choose View", ["FAOSTAT Baselines Explorer", "Raw Data Explorer", "Climate & Location Analytics"])
active_food_class = st.sidebar.selectbox(
    "Data Grouping",
    options=FOOD_CLASS_GROUPS,
    index=FOOD_CLASS_GROUPS.index("FOOD"),
    help="FOOD = edible crops (active) · FOOD_GRADE_OIL = edible oils · NON_EDIBLE = industrial/non-food (for later)",
)

with st.spinner("Parsing local FAOSTAT CSV files and telemetry metrics..."):
    raw_datasets, baseline_df, merged_df = load_pipeline_data(active_food_class)

if app_mode == "FAOSTAT Baselines Explorer":
    st.subheader("📊 Local FAOSTAT CSV Production & Yield Baselines (Kenya)")
    
    if not baseline_df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records Parsed", len(baseline_df))
        with col2:
            st.metric("Reporting Year", int(baseline_df["data_year"].iloc[0]) if "data_year" in baseline_df.columns else 2024)
        with col3:
            st.metric("Unique Elements", baseline_df["element"].nunique() if "element" in baseline_df.columns else 0)

        st.dataframe(baseline_df, use_container_width=True)

        if "expected_yield_tons" in baseline_df.columns:
            st.markdown("### Top Crops by Volume / Yield")
            top_crops = baseline_df.sort_values(by="expected_yield_tons", ascending=False).head(10)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(data=top_crops, x="expected_yield_tons", y="crop_type", palette="viridis", ax=ax)
            ax.set_title("Top Crops from Local FAOSTAT Files")
            ax.set_xlabel("Value / Yield")
            ax.set_ylabel("Crop Type")
            st.pyplot(fig)
    else:
        st.warning("No baseline data found in local FAOSTAT CSV files.")

elif app_mode == "Raw Data Explorer":
    st.subheader("📁 Raw FAOSTAT & Telemetry CSV Files Explorer")
    if raw_datasets:
        selected_file = st.selectbox("Select CSV File", list(raw_datasets.keys()))
        df_selected = raw_datasets[selected_file]
        
        st.write(f"**Shape:** {df_selected.shape[0]} rows, {df_selected.shape[1]} columns")
        st.dataframe(df_selected.head(100), use_container_width=True)
    else:
        st.warning("No CSV files discovered.")

elif app_mode == "Climate & Location Analytics":
    st.subheader("🗺️ Climate & Location Integration")
    st.markdown("Processed telemetry data featuring extracted geographic locations and regional zones.")
    
    if not merged_df.empty:
        st.dataframe(merged_df, use_container_width=True)
        
        if "location" in merged_df.columns and "Temperature_C" in merged_df.columns:
            st.markdown("### Temperature Readings by Location")
            fig, ax = plt.subplots(figsize=(10, 4))
            sns.barplot(data=merged_df, x="location", y="Temperature_C", palette="coolwarm", ax=ax)
            ax.set_title("Temperature (°C) across Ingested Locations")
            ax.set_xlabel("Location")
            ax.set_ylabel("Temperature (°C)")
            plt.xticks(rotation=45)
            st.pyplot(fig)
    else:
        st.warning("No integrated dataset available.")