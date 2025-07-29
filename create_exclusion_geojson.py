import pandas as pd
import json

# === Step 1: Load Data ===
csv_path = "data/raw/LA_Exclusions_Popup_Enriched.csv"
geojson_path = "data/processed/LASuspensionrate.geojson"
output_path = "data/processed/LA_Exclusions_Enriched.geojson"

df = pd.read_csv(csv_path)
with open(geojson_path, 'r') as f:
    geojson = json.load(f)

# === Step 2: Convert list of features into dict by LA code ===
feature_map = {f["properties"]["CTYUA24CD"]: f for f in geojson["features"]}

# === Step 3: Merge DataFrame with GeoJSON properties ===
for _, row in df.iterrows():
    la_code = row["new_la_code"]
    if la_code in feature_map:
        props = feature_map[la_code]["properties"]
        for col in df.columns:
            if col != "new_la_code":
                props[col] = row[col]

# === Step 4: Save new GeoJSON ===
with open(output_path, 'w') as f:
    json.dump(geojson, f)

print("✅ GeoJSON written to:", output_path)