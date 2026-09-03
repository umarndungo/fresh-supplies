"""Canonical crop catalogue loader.

All modules needing the FOOD-crop list / metadata read from a single source of
truth: ``config/crops.yaml``. This module parses it once and exposes the
structures each consumer expects (crop names, FOOD classification, market base
price, spoilage frailty), so there is no duplicated crop list across the repo.
"""

from functools import lru_cache
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - pyyaml is a declared dependency
    yaml = None

CROPS_YAML = Path(__file__).resolve().parent.parent / "config" / "crops.yaml"


@lru_cache(maxsize=1)
def load_crops() -> list[dict]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load the crop catalogue.")
    with open(CROPS_YAML, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return [dict(c) for c in data["crops"]]


def crop_names() -> list[str]:
    return [c["name"] for c in load_crops()]


def crop_food_class() -> dict[str, str]:
    return {c["name"]: c["food_class"] for c in load_crops()}


def crop_base_price_kes() -> dict[str, float]:
    return {c["name"]: float(c["base_price_kes"]) for c in load_crops()}


def spoilage_frailty() -> dict[str, float]:
    return {c["name"]: float(c["spoilage_frailty"]) for c in load_crops()}


# Convenience aliases matching the historical module-level constants so
# downstream code keeps working unchanged.
CROPS = load_crops()
CROP_NAMES = crop_names()
CROP_FOOD_CLASS = crop_food_class()
CROP_BASE_PRICE_KES = crop_base_price_kes()
SPOILAGE_FRAILTY = spoilage_frailty()
