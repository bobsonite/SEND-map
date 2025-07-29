import pandas as pd
import geopandas as gpd

# Load the enriched exclusions data
df = pd.read_csv("data/raw/LA_Exclusions_Popup_Enriched.csv")

# Load the LA boundary geometry
geo = gpd.read_file("data/processed/LASuspensionrate.geojson")

# Merge on new LA code
merged = geo.merge(df, left_on="CTYUA24CD", right_on="new_la_code", how="left")
merged = merged.drop(columns=["new_la_code"])

# Clean NaNs (convert to null in JSON)
merged = merged.where(pd.notnull(merged), None)

# Write cleaned, valid GeoJSON
output_path = "data/processed/LA_Exclusions_Enriched.geojson"
merged.to_file(output_path, driver="GeoJSON")

print(f"✅ GeoJSON written: {output_path}")