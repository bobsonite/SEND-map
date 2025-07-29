import pandas as pd
import geopandas as gpd

# === Step 1: Load CSV and GeoJSON ===
print("Loading data...")
csv_path = "data/processed/LA_exc_susp.csv"
geojson_path = "data/processed/LASuspensionrate.geojson"

df = pd.read_csv(csv_path)
gdf = gpd.read_file(geojson_path)

# === Step 2: Prepare Key Columns ===
df["la_name"] = df["la_name"].str.strip().str.lower()
gdf["la_name"] = gdf["la_name"].str.strip().str.lower()

# === Step 3: Merge on LA Name ===
print("Merging...")
merged = gdf.merge(df, on="la_name", how="left")

# === Step 4: Save GeoJSON ===
output_path = "data/processed/LA_exc_susp.geojson"
merged.to_file(output_path, driver="GeoJSON")

print(f"✅ File created at: {output_path}")