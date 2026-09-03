"""GeoTIFF Climate Raster Ingestion Module."""

import os
import numpy as np
import pandas as pd
import rasterio


def sample_geotiff_at_coordinates(
    tif_path: str, df: pd.DataFrame, lat_col="latitude", lon_col="longitude"
) -> pd.DataFrame:
  """Samples pixel values from a GeoTIFF raster based on telemetry GPS coordinates."""
  result_df = df.copy()

  if not tif_path.startswith("/vsicurl/") and not os.path.exists(tif_path):
    print(f"[Warning] Climate GeoTIFF not found at path: {tif_path}")
    result_df["hot_days_frequency_34C"] = np.nan
    return result_df

  try:
    with rasterio.open(tif_path) as src:
      coords = zip(result_df[lon_col], result_df[lat_col])
      sampled_values = [val[0] for val in src.sample(coords)]

      nodata = src.nodata
      clean_values = [
          np.nan if (nodata is not None and v == nodata) else v
          for v in sampled_values
      ]

      result_df["hot_days_frequency_34C"] = clean_values

  except Exception as e:
    print(f"[Error] Failed to process GeoTIFF {tif_path}: {e}")
    result_df["hot_days_frequency_34C"] = np.nan

  return result_df


def compute_raster_thermal_risk(df: pd.DataFrame) -> pd.DataFrame:
  """Calculates spatial risk exposure based on extracted raster metrics."""
  result_df = df.copy()
  if "hot_days_frequency_34C" in result_df.columns:
    result_df["high_heat_risk_zone"] = (
        result_df["hot_days_frequency_34C"] > 15.0
    )
  else:
    result_df["high_heat_risk_zone"] = False
  return result_df