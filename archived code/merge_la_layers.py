import geopandas as gpd
import pandas as pd
import os

# File paths
geojson_path = os.path.expanduser("~/Documents/SEND-map/data/processed/LASuspensionrate.geojson")
csv_path = os.path.expanduser("~/Documents/SEND-map/data/raw/LA_SEND_ParentInterpretation_Cleaned.csv")
output_path = os.path.expanduser("~/Documents/SEND-map/data/processed/LA_SEND_Merged.geojson")

# Load files
gdf = gpd.read_file(geojson_path)
df = pd.read_csv(csv_path)

# Normalise LA name casing/spacing
gdf["la_name"] = gdf["la_name"].str.strip().str.lower()
df["la_name"] = df["la_name"].str.strip().str.lower()

# Columns to merge (validated from your list)
cols_to_add = [
    "sen_support_percent",
    "ehc_plan_percent",
    "inclusion_rate",
    "region_sen_support_avg",
    "region_ehcp_avg",
    "region_inclusion_avg",
    "parent_interpretation"
]

# Merge
merged = gdf.merge(df[["la_name"] + cols_to_add], on="la_name", how="left")

# Fill missing values
for col in cols_to_add:
    merged[col] = merged[col].fillna("Not available")

# Save to new file
merged.to_file(output_path, driver="GeoJSON")

print(f"✅ Merged LA GeoJSON saved to:\n{output_path}")