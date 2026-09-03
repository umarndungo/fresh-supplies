"""
FAOSTAT Local Source Ingestion Module
Parses local FAOSTAT Africa production and auxiliary lookup files directly from disk.
"""

from pathlib import Path
import pandas as pd


# FAOSTAT Item Codes that represent livestock, animal products, and animal
# aggregates. The "Production_Crops_Livestock" domain bundles crops AND animals
# into one file, so we exclude these to keep only plant/crop items.
LIVESTOCK_ITEM_CODES = {
    # Live animals & primary livestock products (raw codes < 1000)
    866, 867, 868, 869, 882, 885, 886, 887, 888, 889, 894, 897, 898, 899, 900, 901, 919,
    976, 977, 978, 979, 982, 987, 995,
    1016, 1017, 1018, 1019, 1020, 1025, 1034, 1035, 1036, 1037, 1043,
    1057, 1058, 1062, 1096, 1126, 1127, 1128, 1129, 1130, 1140, 1141, 1163,
    1181, 1182, 1183, 1225, 1242,
    # Livestock aggregates (codes >= 1717)
    1745, 1746, 1749, 1765, 1780, 1783, 1806, 1807, 1808, 1809, 1811, 1816, 2029,
}


def _is_livestock(item_code) -> bool:
    """Returns True if the FAOSTAT item code maps to livestock/animal products."""
    try:
        return int(float(item_code)) in LIVESTOCK_ITEM_CODES
    except (TypeError, ValueError):
        return False


# Human-consumption classification for the plant/crop items that remain after
# the livestock filter. Three buckets: FOOD (edible crops), FOOD_GRADE_OIL
# (edible oil-bearing seeds/oils), NON_EDIBLE (industrial / non-food / processed
# derived products that are not target market crops).
FOOD_ITEM_CODES = {
    15, 27, 44, 56, 75, 79, 83,                      # cereals
    116, 122, 125, 137, 149,                         # roots & tubers
    156,                                             # sugar cane
    176, 191, 195, 197, 201, 211,                    # pulses (dry)
    217, 234, 249,                                   # nuts & coconut
    358, 366, 367, 372, 373, 388, 393, 397, 401, 403, 406, 407, 414, 417, 420, 426, 430, 463,  # vegetables
    486, 489, 490, 495, 497, 507, 512, 515, 521, 526, 534, 536, 544, 558, 567, 571, 572, 574, 577, 600, 603, 619,  # fruits
    656, 667, 675,                                   # coffee & tea
    687, 689, 692, 698, 702, 711, 720, 723,          # spices & stimulants (food)
    1717, 1720, 1723, 1726, 1729, 1735, 1738, 1804,  # crop aggregates
}

FOOD_GRADE_OIL_ITEM_CODES = {
    236, 242, 267, 268, 289,                         # soy, groundnut, sunflower (seed+oil), sesame
    252,                                             # coconut oil
    331,                                             # cottonseed oil
    60,                                              # oil of maize (corn oil)
    270,                                             # rape/colza seed
    339,                                             # other oil seeds n.e.c.
    1732, 1841,                                      # oilcrop aggregates
}

NON_EDIBLE_ITEM_CODES = {
    226,                                             # areca/betel nut (narcotic chew)
    265,                                             # castor oil seeds (industrial)
    328, 329, 767,                                   # cotton (seed/lint) — fibre
    333, 334,                                        # linseed & linseed oil (industrial)
    789, 809,                                        # sisal, abaca (fibre)
    826,                                             # tobacco
    754,                                             # pyrethrum (insecticide)
    51,                                              # beer of barley (malted/processed)
    162, 165,                                        # raw sugar, molasses (processed)
    17530,                                           # fibre crops aggregate
}


def _food_class(item_code) -> str:
    """Classifies a crop item code into FOOD / FOOD_GRADE_OIL / NON_EDIBLE."""
    try:
        code = int(float(item_code))
    except (TypeError, ValueError):
        return "FOOD"
    if code in FOOD_ITEM_CODES:
        return "FOOD"
    if code in FOOD_GRADE_OIL_ITEM_CODES:
        return "FOOD_GRADE_OIL"
    return "NON_EDIBLE"


def load_faostat_local_sources(data_dir: str = None) -> dict:
    """Loads all core FAOSTAT local files from storage into a dictionary of DataFrames."""
    print("[Info] Loading FAOSTAT source files from local storage...")
    
    # Force absolute path resolution to data/raw based on project structure
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    target_dir = project_root / "data" / "raw"
    
    files = {
        "main_data": "FAOSTAT_data_en_8-19-2026.csv",
        "africa_wide": "Production_Crops_Livestock_E_Africa.csv",
        "africa_noflag": "Production_Crops_Livestock_E_Africa_NOFLAG.csv",
        "items": "Production_Crops_Livestock_E_ItemCodes.csv",
        "areas": "Production_Crops_Livestock_E_AreaCodes.csv",
        "elements": "Production_Crops_Livestock_E_Elements.csv",
        "flags": "Production_Crops_Livestock_E_Flags.csv"
    }
    
    loaded_datasets = {}
    for key, filename in files.items():
        path = target_dir / filename
        if path.exists():
            try:
                loaded_datasets[key] = pd.read_csv(path, encoding="latin1", low_memory=False)
                print(f"  [Loaded] {filename} ({loaded_datasets[key].shape[0]} rows)")
            except Exception as e:
                print(f"  [Error] Failed to load {filename}: {e}")
        else:
            print(f"  [Warning] File not found: {filename} at {path}")
            
    return loaded_datasets


def get_faostat_baseline_for_country(country_name: str = "Kenya", target_year: int = 2024, data_dir: str = None) -> pd.DataFrame:
    """Extracts and standardizes baseline production and yield metrics from local FAOSTAT CSVs."""
    datasets = load_faostat_local_sources(data_dir)
    
    if "africa_wide" in datasets:
        df = datasets["africa_wide"]
        country_df = df[df["Area"].str.lower() == country_name.lower()].copy()
        # Keep only plant/crop items — drop livestock & animal products
        country_df = country_df[~country_df["Item Code"].map(_is_livestock)]

        if country_df.empty:
            print(f"[Warning] Country '{country_name}' not found in Africa dataset.")
            return pd.DataFrame()
            
        year_col = f"Y{target_year}"
        flag_col = f"Y{target_year}F"
        
        standardized = pd.DataFrame()
        standardized["crop_type"] = country_df["Item"]
        standardized["item_code"] = country_df.get("Item Code", country_df.get("Item Code (CPC)", None))
        standardized["food_class"] = country_df["Item Code"].map(_food_class)
        standardized["Zone"] = country_df["Area"]
        standardized["element"] = country_df["Element"]
        
        if year_col in country_df.columns:
            standardized["value"] = pd.to_numeric(country_df[year_col], errors="coerce").fillna(0.0)
        else:
            standardized["value"] = 0.0
            
        if flag_col in country_df.columns:
            standardized["flag"] = country_df[flag_col]
        else:
            standardized["flag"] = ""
            
        standardized["unit"] = country_df["Unit"]
        standardized["data_year"] = target_year
        standardized["expected_yield_tons"] = standardized["value"] if "tonnes" in str(standardized["unit"].iloc[0]).lower() else standardized["value"] / 1000.0
        
        print(f"[Success] Extracted {len(standardized)} standardized baseline records for {country_name} ({target_year}).")
        return standardized
        
    elif "main_data" in datasets:
        df = datasets["main_data"]
        country_df = df[(df["Area"].str.lower() == country_name.lower()) & (df["Year"] == target_year)].copy()
        
        standardized = pd.DataFrame()
        standardized["crop_type"] = country_df["Item"]
        standardized["Zone"] = country_df["Area"]
        standardized["element"] = country_df["Element"]
        standardized["value"] = pd.to_numeric(country_df["Value"], errors="coerce").fillna(0.0)
        standardized["unit"] = country_df["Unit"]
        standardized["data_year"] = target_year
        standardized["expected_yield_tons"] = standardized["value"]
        return standardized
        
    return pd.DataFrame()