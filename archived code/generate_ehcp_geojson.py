import geopandas as gpd
import pandas as pd

# Load files
geo = gpd.read_file("data/processed/LASuspensionrate.geojson")
csv = pd.read_csv("data/raw/EHCPplanprocessLAL.csv")

# Clean join key
geo["la_name_clean"] = geo["la_name"].str.lower().str.strip()
csv["la_name_clean"] = csv["la_name"].str.lower().str.strip()

# Merge on clean name
merged = geo.merge(csv, on="la_name_clean", how="left").drop(columns=["la_name_clean"])

# Replace NaNs with None (valid in GeoJSON)
merged = merged.where(pd.notnull(merged), None)

# Save
merged.to_file("data/processed/EHCP_Timeliness.geojson", driver="GeoJSON")
print("✅ Clean GeoJSON exported with", len(merged), "features.")