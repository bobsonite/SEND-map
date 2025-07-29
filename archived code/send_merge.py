import pandas as pd
import json
import os

# Define file paths
geojson_path = os.path.expanduser("~/Documents/SEND-map/data/processed/OpenSchoolsSL_Scores.geojson")
csv_path = os.path.expanduser("~/Documents/SEND-map/data/processed/School_InclusionMetrics.csv")
output_path = os.path.expanduser("~/Documents/SEND-map/data/processed/OpenSchoolsSL_SEND.geojson")

# Load GeoJSON
with open(geojson_path, 'r') as f:
    geojson_data = json.load(f)

# Load CSV
df = pd.read_csv(csv_path)

# Build lookup dictionary
lookup = {}
for _, row in df.iterrows():
    name = str(row['EstablishmentName']).strip().lower()
    lookup[name] = {
        "FSM": "Not available" if pd.isna(row['FSM']) else row['FSM'],
        "SENSupportPercent": "Not available" if pd.isna(row['SENSupportPercent']) else row['SENSupportPercent'],
        "EHCPPercent": "Not available" if pd.isna(row['EHCPPercent']) else row['EHCPPercent']
    }

# Merge into GeoJSON
for feature in geojson_data['features']:
    props = feature['properties']
    school_name = str(props.get('EstablishmentName', '')).strip().lower()
    match = lookup.get(school_name, {
        "FSM": "Not available",
        "SENSupportPercent": "Not available",
        "EHCPPercent": "Not available"
    })
    props['FSM'] = match['FSM']
    props['SENSupportPercent'] = match['SENSupportPercent']
    props['EHCPPercent'] = match['EHCPPercent']

# Save output
with open(output_path, 'w') as f:
    json.dump(geojson_data, f, indent=2)

print("✅ GeoJSON merge completed and saved as:", output_path)