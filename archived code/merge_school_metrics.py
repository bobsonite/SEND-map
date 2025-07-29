
import json
import pandas as pd

# File paths
geojson_path = "data/processed/OpenSchoolsSL_Scores.geojson"
csv_path = "data/processed/School_InclusionMetrics.csv"
output_path = "data/processed/OpenSchoolsSL_SEND.geojson"

# Load GeoJSON
with open(geojson_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Load CSV
df = pd.read_csv(csv_path)

# Build lookup dict using EstablishmentName
lookup = {}
for _, row in df.iterrows():
    name = row.get("EstablishmentName")
    if name and name not in lookup:
        lookup[name] = {
            "FSM": row.get("FSM", "Not available"),
            "SENSupportPercent": row.get("SENSupportPercent", "Not available"),
            "EHCPPercent": row.get("EHCPPercent", "Not available")
        }

# Inject values into geojson features
for feature in geojson_data["features"]:
    props = feature.get("properties", {})
    name = props.get("EstablishmentName")
    if name in lookup:
        props["FSM"] = lookup[name].get("FSM", "Not available")
        props["SENSupportPercent"] = lookup[name].get("SENSupportPercent", "Not available")
        props["EHCPPercent"] = lookup[name].get("EHCPPercent", "Not available")
    else:
        props["FSM"] = "Not available"
        props["SENSupportPercent"] = "Not available"
        props["EHCPPercent"] = "Not available"

# Write output
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(geojson_data, f, ensure_ascii=False, indent=2)

print("✅ Successfully created:", output_path)
