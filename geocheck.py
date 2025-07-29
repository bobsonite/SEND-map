import json

geo_path = "/Users/saaj/Documents/SEND-map/data/processed/OpenSchoolsSL_SEND.geojson"

with open(geo_path, "r") as f:
    data = json.load(f)

names = [f["properties"].get("EstablishmentName") for f in data["features"]]
print("🔢 Total features:", len(names))
print("🧠 Unique school names:", len(set(names)))