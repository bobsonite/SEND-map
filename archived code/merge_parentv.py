import json
import pandas as pd

# === File paths ===
geojson_path = "data/processed/OpenSchoolsSL_with_SEN_withProvision.geojson"
csv_path = "data/raw/Weighted_Sentiment_Scores.csv"  # path to your new CSV
output_path = "data/processed/OpenSchoolsSL_Scores.geojson"

# === Load GeoJSON ===
with open(geojson_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# === Load final sentiment scores CSV ===
df = pd.read_csv(csv_path)

# === Clean and deduplicate ===
df = df.drop_duplicates(subset="School Name", keep="first")

# === Convert to lookup dictionary ===
score_columns = [col for col in df.columns if col.startswith("ParentView_Q")]
score_lookup = df.set_index("School Name")[score_columns].to_dict(orient="index")

# === Inject scores into GeoJSON ===
for feature in geojson_data["features"]:
    props = feature.get("properties", {})
    school_name = props.get("EstablishmentName")

    if school_name in score_lookup:
        for q, value in score_lookup[school_name].items():
            props[q] = value
    else:
        for q in score_columns:
            props[q] = None

# === Save to new GeoJSON ===
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(geojson_data, f, indent=2)

print(f"✅ Created: {output_path}")