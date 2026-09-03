"""Configuration settings and operational constants."""

# Status Efficiency Thresholds (%)
EFFICIENCY_NORMAL_THRESHOLD = 90.0
EFFICIENCY_WARNING_THRESHOLD = 70.0

# Cleaning & Outlier Boundaries
TEMP_MIN_C = -50.0
TEMP_MAX_C = 70.0
PRESSURE_MIN_PSI = 0.0
PRESSURE_MAX_PSI = 3000.0

# Categorical Mappings
ZONE_MAPPINGS = {
    "ZONE_CENTRAL": "Zone_Central",
    "CENTRAL ZONE": "Zone_Central",
    "ZONE_NORTH": "Zone_North",
    "NORTH ZONE": "Zone_North",
    "ZONE_WEST": "Zone_West",
    "WEST ZONE": "Zone_West",
    "ZONE_EAST": "Zone_East",
    "EAST ZONE": "Zone_East",
    "ZONE_SOUTH": "Zone_South",
    "SOUTH ZONE": "Zone_South",
    "NAN": "Zone_Central",
}