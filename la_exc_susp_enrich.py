import pandas as pd
import geopandas as gpd

# === PATHS ===
csv_path = "/Users/saaj/Documents/SEND-map/data/raw/Exc_sus1.csv"
geojson_path = "/Users/saaj/Documents/SEND-map/data/processed/LASuspensionrate.geojson"
output_path = "/Users/saaj/Documents/SEND-map/data/processed/LA_ExcSus_Merged.geojson"

# === LOAD FILES ===
df = pd.read_csv(csv_path)
gdf = gpd.read_file(geojson_path)

# === PREPARE COLUMNS FOR JOIN ===
df['Row Labels'] = df['Row Labels'].astype(str)
gdf['CTYUA24CD'] = gdf['CTYUA24CD'].astype(str)

# === MERGE ===
merged = gdf.merge(df, how='left', left_on='CTYUA24CD', right_on='Row Labels')

# === EXPORT ===
merged.to_file(output_path, driver='GeoJSON')

print(f"✅ Merged file saved to: {output_path}")
