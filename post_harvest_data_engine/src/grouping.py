"""
Data grouping by food classification.

Separates datasets into three independent groupings based on their food class:
  - FOOD           (edible crops / food stuffs)
  - FOOD_GRADE_OIL (edible oil-bearing seeds & oils)
  - NON_EDIBLE     (industrial / non-food crops)

Each grouping is written to its own processed sub-directory so the categories
stay cleanly separated. The FOOD grouping is the active working set; the other
two are scaffolded for later use.
"""

from pathlib import Path

import pandas as pd

from .faostat_downloader import get_faostat_baseline_for_country
from .ingestion import merge_all_sources

FOOD_CLASSES = ("FOOD", "FOOD_GRADE_OIL", "NON_EDIBLE")

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def _group_dir(food_class: str) -> Path:
    """Returns the processed sub-directory for a given food class."""
    mapping = {
        "FOOD": "food",
        "FOOD_GRADE_OIL": "food_grade_oil",
        "NON_EDIBLE": "non_edible",
    }
    return PROCESSED_DIR / mapping[food_class]


def write_groupings(
    baseline_df: pd.DataFrame,
    merged_df: pd.DataFrame,
    *,
    food_classes: tuple[str, ...] = FOOD_CLASSES,
) -> dict:
    """Writes separate per-category files for the baseline and merged datasets.

    For each food class, exports:
      - <group>/faostat_food_<class>.csv      (baseline records of that class)
      - <group>/integrated_post_harvest_<class>.csv  (merged records of that class)

    Returns a mapping of food_class -> dict of exported file paths.
    """
    exported = {}
    for food_class in food_classes:
        group_dir = _group_dir(food_class)
        group_dir.mkdir(parents=True, exist_ok=True)

        baseline_file = group_dir / f"faostat_{food_class.lower()}.csv"
        baseline_class = baseline_df[baseline_df["food_class"] == food_class] \
            if "food_class" in baseline_df.columns else baseline_df.iloc[0:0]
        baseline_class.to_csv(baseline_file, index=False)

        merged_file = group_dir / f"integrated_post_harvest_{food_class.lower()}.csv"
        merged_class = merged_df[merged_df["food_class"] == food_class] \
            if "food_class" in merged_df.columns else merged_df.iloc[0:0]
        merged_class.to_csv(merged_file, index=False)

        group_outputs = {
            "baseline": str(baseline_file),
            "merged": str(merged_file),
        }

        # For the active FOOD grouping, attach market pricing & destinations.
        if food_class == "FOOD" and not merged_class.empty:
            from .market_pricing import write_market_outputs
            annotated = write_market_outputs(merged_class, group_dir)
            group_outputs.update(
                {
                    "market_destinations": str(group_dir / "market_destinations.csv"),
                    "market_prices": str(group_dir / "market_prices.csv"),
                    "market_annotated": str(group_dir / "food_market_annotated.csv"),
                }
            )

        exported[food_class] = group_outputs
        print(
            f"[Grouping {food_class}] baseline={len(baseline_class):,} rows -> "
            f"{baseline_file} | merged={len(merged_class):,} rows -> {merged_file}"
        )

    return exported


def build_and_write_groupings(
    country_name: str = "Kenya",
    target_year: int = 2024,
    data_dir: str = None,
    *,
    telemetry_df: pd.DataFrame = None,
    food_classes: tuple[str, ...] = ("FOOD",),
) -> dict:
    """Runs ingestion, then separates baseline + merged data into groupings.

    Only the supplied food_classes are written (defaults to FOOD, the active set).

    If telemetry_df is not provided, it falls back to the existing on-disk
    processed integrated dataset (data/processed/integrated_post_harvest_dataset.csv)
    so the 10,000-row sensor dataset is used rather than the small fallback.
    """
    baseline_df = get_faostat_baseline_for_country(
        country_name=country_name, target_year=target_year, data_dir=data_dir
    )

    if telemetry_df is None:
        on_disk = PROCESSED_DIR / "integrated_post_harvest_dataset.csv"
        telemetry_df = pd.read_csv(on_disk) if on_disk.exists() else None

    merged_df = merge_all_sources(
        telemetry_df=telemetry_df,
        country_name=country_name,
        target_year=target_year,
        data_dir=data_dir,
    )
    return write_groupings(baseline_df, merged_df, food_classes=food_classes)


def load_grouped_dataset(food_class: str = "FOOD") -> pd.DataFrame:
    """Loads the merged dataset for a given food class (default: FOOD)."""
    mapping = {"FOOD": "food", "FOOD_GRADE_OIL": "food_grade_oil", "NON_EDIBLE": "non_edible"}
    path = PROCESSED_DIR / mapping[food_class] / f"integrated_post_harvest_{food_class.lower()}.csv"
    if not path.exists():
        raise FileNotFoundError(f"No grouped dataset found at {path}")
    return pd.read_csv(path)


if __name__ == "__main__":
    build_and_write_groupings()
