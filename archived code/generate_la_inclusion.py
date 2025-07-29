import pandas as pd
import os

# Set paths
input_path = os.path.expanduser("~/Downloads/data-special-educational-needs-in-england (2).csv")
output_path = os.path.expanduser("~/Documents/SEND-map/data/processed/LA_SEND_InclusionModel.csv")

# Load data
df = pd.read_csv(input_path)

# Filter to LA-level totals only
filtered = df[
    (df["geographic_level"] == "Local authority") &
    (df["phase_type_grouping"] == "Total") &
    (df["type_of_establishment"] == "Total")
]

# Select latest year
latest_year = filtered["time_period"].max()
latest = filtered[filtered["time_period"] == latest_year].copy()

# Add inclusion ratio
latest["inclusion_ratio"] = pd.to_numeric(latest["sen_support_percent"], errors='coerce') / \
                            pd.to_numeric(latest["ehc_plan_percent"], errors='coerce')

# Add interpretation
def interpret(row):
    if row["inclusion_ratio"] > 4:
        return "High support, low EHCP – early intervention model"
    elif row["inclusion_ratio"] > 2:
        return "Balanced support and plans"
    elif row["inclusion_ratio"] > 1:
        return "Higher EHCP share – complex need system"
    else:
        return "Unusually EHCP-heavy – may reflect stricter support access"

latest["interpretation"] = latest.apply(interpret, axis=1)

# Export
latest[[
    "la_name", "sen_support_percent", "ehc_plan_percent", "inclusion_ratio", "interpretation"
]].sort_values(by="inclusion_ratio", ascending=False).to_csv(output_path, index=False)

print("✅ File saved to:", output_path)