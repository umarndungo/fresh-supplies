"""Spatial-temporal feature engineering and efficiency classification."""

import pandas as pd


def calculate_efficiency(
    actual_output: float, target_output: float
) -> float:
  """Calculates operational efficiency percentage."""
  if target_output == 0:
    return 0.0
  return (actual_output / target_output) * 100.0


def get_operational_status(efficiency: float) -> str:
  """Classifies site status based on target output efficiency."""
  if efficiency >= 90.0:
    return "Normal"
  elif efficiency >= 70.0:
    return "Warning"
  return "Critical"


def engineer_pipeline_features(df: pd.DataFrame) -> pd.DataFrame:
  """Generates transit risk metrics and rolling operational baselines."""
  df_time = df.set_index("timestamp").sort_index()

  if "Temperature_C" in df_time.columns:
    df_time["Temp_24h_Rolling_Avg"] = (
        df_time["Temperature_C"].rolling(window=24, min_periods=1).mean()
    )

  if "Transit_Duration_Hr" in df_time.columns:
    df_time["Thermal_Heat_Exposure"] = (
        df_time["Temperature_C"] * df_time["Transit_Duration_Hr"]
    )

  return df_time.reset_index()