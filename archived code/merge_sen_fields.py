import json
import pandas as pd

# === File paths: DO NOT overwrite the current working file ===
geojson_path = "data/processed/OpenSchoolsSL_with_SEN.geojson"
csv_path = "data/raw/Simplified_SEN_Provision_List.csv"
output_path = "data/processed/OpenSchoolsSL_with_SEN_withProvision.geojson"

# === Load the school-level GeoJSON ===
with open(geojson_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# === Load the simplified SEN provision CSV ===
df_sen = pd.read_csv(csv_path)

# === Convert to lookup dict for efficient matching ===
sen_lookup = {}
for _, row in df_sen.iterrows():
    name = row["EstablishmentName"]
    # only use the first occurrence of each name
    if name not in sen_lookup:
        sen_lookup[name] = {
            "SEN_Provision_List": row["SEN_Provision_List"],
            "HasSENProvision": row["HasSENProvision"]
        }

# === Add SEN info to the geojson properties ===
for feature in geojson_data["features"]:
    props = feature.get("properties", {})
    school_name = props.get("EstablishmentName")

    match = sen_lookup.get(school_name)
    if match:
        props["SEN_Provision_List"] = match["SEN_Provision_List"]
        props["HasSENProvision"] = bool(match["HasSENProvision"])
    else:
        props["SEN_Provision_List"] = "Not available"
        props["HasSENProvision"] = False

# === Save a new geojson file ===
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(geojson_data, f, indent=2)

print(f"✅ Created: {output_path}")