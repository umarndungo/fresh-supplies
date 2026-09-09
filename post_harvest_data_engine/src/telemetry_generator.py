"""
Synthetic Telemetry Generator for Agricultural Transit Routes.
Generates realistic vehicle telemetry logs with diurnal temperature modeling, 
sensor outlier noise, and coordinate-derived location strings.
"""

import os
import numpy as np
import pandas as pd

from src.crops import crop_names as _crop_names


def extract_location_from_coords(lat, lon) -> str:
    """Converts numeric latitude and longitude into a clean cardinal location format."""
    if pd.isna(lat) or pd.isna(lon):
        return "Unknown Location"
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return f"{abs(lat):.2f}°{ns}, {abs(lon):.2f}°{ew}"


def generate_raw_telemetry(
    num_records: int = 10000,
    output_path: str = "data/raw/raw_telemetry.csv",
    seed: int = 42,
) -> pd.DataFrame:
  """Generates realistic vehicle telemetry logs, injects outlier noise, and exports them."""
  np.random.seed(seed)
  
  dir_name = os.path.dirname(output_path)
  if dir_name:
      os.makedirs(dir_name, exist_ok=True)

  zones = ["ZONE_CENTRAL", "ZONE_NORTH", "ZONE_SOUTH", "ZONE_EAST"]
  shifts = ["Morning", "Afternoon", "Night"]

  # Crop list comes from the single source of truth (config/crops.yaml).
  crops = _crop_names()

  lats = np.random.uniform(-3.5, 1.0, num_records)
  lons = np.random.uniform(34.5, 37.5, num_records)

  start_date = pd.Timestamp("2026-08-01")
  time_offsets = np.random.uniform(0, 10 * 24 * 3600, num_records)
  timestamps = [start_date + pd.Timedelta(seconds=s) for s in time_offsets]

  hours = np.array([ts.hour for ts in timestamps])
  base_temps = 20.0 + 8.0 * np.sin((hours - 6) * np.pi / 12)
  temps = base_temps + np.random.normal(0, 2.5, num_records)

  outlier_idx = np.random.choice(num_records, size=int(num_records * 0.015), replace=False)
  temps[outlier_idx] = np.random.choice([88.0, -25.0], size=len(outlier_idx))

  pressures = np.random.normal(32.0, 1.5, num_records)
  relative_humidity = np.clip(
      78.0 - (temps - 20.0) * 2.0 + np.random.normal(0, 6.0, num_records),
      25.0,
      100.0,
  )
  rainfall_intensity = np.maximum(
      0.0,
      np.random.gamma(shape=1.2, scale=2.0, size=num_records)
      * (relative_humidity > 82.0),
  )
  vehicle_speed = np.clip(np.random.normal(38.0, 9.0, num_records), 8.0, 70.0)
  route_distance = np.round(np.random.uniform(20.0, 280.0, num_records), 2)
  stopover_duration = np.round(np.random.exponential(0.75, num_records), 2)
  transit_duration = np.round(route_distance / vehicle_speed + stopover_duration, 2)
  baseline_losses = np.random.uniform(8.0, 18.0, num_records)

  df = pd.DataFrame({
      "timestamp": timestamps,
      "Zone": np.random.choice(zones, num_records),
      "crop_type": np.random.choice(crops, num_records),
      "latitude": lats,
      "longitude": lons,
      "Temperature_C": np.round(temps, 2),
      "Pressure_PSI": np.round(pressures, 2),
      "Relative_Humidity_Pct": np.round(relative_humidity, 2),
      "Rainfall_Intensity_Mm": np.round(rainfall_intensity, 2),
      "Vehicle_Speed_Kmh": np.round(vehicle_speed, 2),
      "Route_Distance_Km": route_distance,
      "Stopover_Duration_Hr": stopover_duration,
      "Transit_Duration_Hr": transit_duration,
      "Vehicle_Category": np.random.choice(
          ["Motorbike", "Pickup", "Light Truck", "Refrigerated Truck"],
          num_records,
          p=[0.12, 0.38, 0.38, 0.12],
      ),
      "Shift": np.random.choice(shifts, num_records),
      "baseline_loss_pct": np.round(baseline_losses, 2)
  })

  df["location"] = df.apply(lambda r: extract_location_from_coords(r["latitude"], r["longitude"]), axis=1)
  df = df.sort_values("timestamp").reset_index(drop=True)

  df.to_csv(output_path, index=False)
  print(f"[Generator] Generated {num_records:,} raw telemetry records -> {output_path}")
  return df


if __name__ == "__main__":
  generate_raw_telemetry(num_records=10000)