"""Master Execution Pipeline Driver.

Produces independent, separated data groupings per food class. The FOOD
grouping is the active working set; FOOD_GRADE_OIL and NON_EDIBLE are
scaffolded for later use.
"""

import os
import pandas as pd

from src.grouping import build_and_write_groupings
from src.telemetry_generator import generate_raw_telemetry


def run_pipeline():
  """Runs the end-to-end ingestion pipeline and writes separated groupings."""
  print("=" * 60)
  print("STARTING POST-HARVEST LOSS DATA ENGINE INGESTION")
  print("=" * 60)

  raw_telemetry_path = "data/raw/raw_telemetry.csv"

  # 1. Generate or load raw telemetry file from disk
  if not os.path.exists(raw_telemetry_path):
    print(f"[Main] {raw_telemetry_path} missing. Generating 10,000 records...")
    telemetry_df = generate_raw_telemetry(
        num_records=10000, output_path=raw_telemetry_path
    )
  else:
    print(f"[Main] Loading raw telemetry dataset from {raw_telemetry_path}...")
    telemetry_df = pd.read_csv(raw_telemetry_path)

  # 2. Separate datasets into per-category groupings (FOOD is the active set)
  groupings = build_and_write_groupings(telemetry_df=telemetry_df)

  # 3. Execution Results Summary
  print("=" * 60)
  print("PIPELINE EXECUTION SUMMARY")
  print("=" * 60)
  for food_class, paths in groupings.items():
    print(f"  {food_class}: {paths}")

  # 4. Export the active FOOD grouping summary
  food = groupings["FOOD"]
  print("\n[Success] Separated groupings exported.")
  print(f"  Baseline : {food['baseline']}")
  print(f"  Merged   : {food['merged']}\n")


if __name__ == "__main__":
  run_pipeline()