"""
Comprehensive Data Ingestion & Spatial Location Pipeline
Processes local FAOSTAT CSV files, telemetry, and CHIRTS climate datasets.
"""

import os
import glob
import numpy as np
import pandas as pd
from .faostat_downloader import get_faostat_baseline_for_country, load_faostat_local_sources, _food_class
from src.crops import crop_food_class as _food_class_from_catalogue


# Map telemetry/merged crop names to a food classification. Defaults to FOOD
# (edible) for known food crops; unknown samples default to FOOD unless the
# crop is explicitly non-edible. The canonical FOOD crops come from the single
# source of truth (config/crops.yaml); historical/synonym names are kept here.
CROP_FOOD_CLASS = {
    **_food_class_from_catalogue(),
    "Maize (corn)": "FOOD",
    "Beans, dry": "FOOD",
}


def _food_class_for_crop(crop_type: str) -> str:
    """Resolves a crop name to FOOD / FOOD_GRADE_OIL / NON_EDIBLE."""
    if pd.isna(crop_type):
        return "FOOD"
    return CROP_FOOD_CLASS.get(str(crop_type).strip(), "FOOD")


def extract_location_from_coords(lat, lon):
    """Extracts a clean, readable location string from coordinates."""
    if pd.isna(lat) or pd.isna(lon):
        return "Unknown Location"
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return f"{abs(lat):.2f}°{ns}, {abs(lon):.2f}°{ew}"


def ingest_all_raw_files(raw_dir: str = "./") -> dict:
    """Scans workspace and ingests all raw CSV mapping tables and telemetry."""
    return load_faostat_local_sources(raw_dir)


def merge_all_sources(
    telemetry_df: pd.DataFrame = None, 
    country_name: str = "Kenya",
    target_year: int = 2024,
    data_dir: str = "./",
    **kwargs
) -> pd.DataFrame:
    """
    Orchestrates ingestion, merges local FAOSTAT baselines with telemetry data,
    and extracts clean location names from coordinates.
    """
    print("\n--- Starting Ingestion & Location Integration Pipeline ---")
    
    # 1. Load real FAOSTAT baseline from local CSV files
    baseline_df = get_faostat_baseline_for_country(country_name=country_name, target_year=target_year, data_dir=data_dir)

    # 2. Process telemetry or fallback integrated dataset
    if telemetry_df is not None and not telemetry_df.empty:
        merged_df = telemetry_df.copy()
    elif os.path.exists("integrated_post_harvest_dataset.csv"):
        merged_df = pd.read_csv("integrated_post_harvest_dataset.csv")
    else:
        merged_df = pd.DataFrame({
            "timestamp": pd.date_range(start="2026-08-01", periods=5, freq="h"),
            "crop_type": ["Maize", "Beans", "Potatoes", "Avocados", "Bananas"],
            "Zone": ["ZONE_EAST", "ZONE_CENTRAL", "ZONE_NORTH", "ZONE_SOUTH", "ZONE_CENTRAL"],
            "latitude": [-1.2863, -0.5238, 0.3031, -1.1722, -0.6792],
            "longitude": [36.8172, 37.9062, 32.5811, 36.9787, 36.0661],
            "Temperature_C": [22.5, 24.1, 19.8, 21.0, 23.4]
        })

    # 3. Extract 'location' from coordinates
    if "latitude" in merged_df.columns and "longitude" in merged_df.columns:
        merged_df["location"] = merged_df.apply(
            lambda row: extract_location_from_coords(row["latitude"], row["longitude"]), axis=1
        )
    else:
        merged_df["location"] = "Unknown Location"

    # 4. Attach food classification (FOOD / FOOD_GRADE_OIL / NON_EDIBLE).
    #    Prefer the FAOSTAT baseline classification; fall back to the
    #    telemetry crop-name mapping for rows not present in the baseline.
    if "crop_type" in merged_df.columns:
        baseline_map = {}
        if not baseline_df.empty and {"crop_type", "food_class"}.issubset(baseline_df.columns):
            baseline_map = dict(zip(baseline_df["crop_type"], baseline_df["food_class"]))
        merged_df["food_class"] = merged_df["crop_type"].map(
            lambda c: baseline_map.get(c, _food_class_for_crop(c))
        )

    print(f"[Success] Processed dataset with {len(merged_df)} records (FAOSTAT baseline rows: {len(baseline_df)}).")
    print("--- Pipeline Integration Complete ---")
    return merged_df


if __name__ == "__main__":
    df_res = merge_all_sources()
    print(df_res.head())