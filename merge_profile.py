import json
import pandas as pd

# File paths
geojson_path = "/Users/saaj/Documents/SEND-map/data/processed/OpenSchoolsSL_SEND_UNIQUE.geojson"
csv_path = "/Users/saaj/Documents/SEND-map/data/raw/School_Profile_Final2.csv"
output_path = "/Users/saaj/Documents/SEND-map/data/processed/OpenSchoolsSL_SEND_MERGED.geojson"

# Load GeoJSON
print("📦 Loading GeoJSON...")
with open(geojson_path, "r", encoding="utf-8") as f:
    geo = json.load(f)

# Load CSV
print("📘 Loading CSV...")
df = pd.read_csv(csv_path)

# Create lookup dictionary from unique School_Name
csv_lookup = df.set_index("School_Name").to_dict(orient="index")

# Filter GeoJSON features to unique EstablishmentName
seen_names = set()
filtered_features = []
for feature in geo["features"]:
    name = feature["properties"].get("EstablishmentName")
    if name and name not in seen_names:
        seen_names.add(name)
        filtered_features.append(feature)
geo["features"] = filtered_features

# Merge CSV fields into GeoJSON features
print("🔄 Merging data...")
matched, unmatched = 0, 0
for feature in geo["features"]:
    name = feature["properties"].get("EstablishmentName")
    if name in csv_lookup:
        for key, value in csv_lookup[name].items():
            feature["properties"][key] = None if pd.isna(value) else value
        matched += 1
    else:
        unmatched += 1

# Save output
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(geo, f)

print(f"\n✅ Merged {matched:,} of {len(geo['features']):,} schools")
print(f"❌ Unmatched rows: {unmatched:,}")
print(f"💾 Saved to: {output_path}")