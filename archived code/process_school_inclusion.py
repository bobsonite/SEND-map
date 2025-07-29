import pandas as pd
import os

# Define input and output paths
input_path = os.path.expanduser("~/Documents/SEND-map/data/raw/SchoolCharacteristicsSL.csv")
output_path = os.path.expanduser("~/Documents/SEND-map/data/processed/School_InclusionMetrics.csv")

# Load the data
df = pd.read_csv(input_path)

# Ensure required columns exist and convert to numeric
df["NumberOfPupils"] = pd.to_numeric(df["NumberOfPupils"], errors="coerce")
df["SENNoStat"] = pd.to_numeric(df["SENNoStat"], errors="coerce")
df["SENStat"] = pd.to_numeric(df["SENStat"], errors="coerce")

# Calculate % SEN Support
df["SENSupportPercent"] = (df["SENNoStat"] / df["NumberOfPupils"]) * 100

# Calculate % EHCP
df["EHCPPercent"] = (df["SENStat"] / df["NumberOfPupils"]) * 100

# Calculate Inclusion Balance Ratio (avoid divide-by-zero)
df["InclusionBalance"] = df["SENSupportPercent"] / df["EHCPPercent"]
df["InclusionBalance"] = df["InclusionBalance"].replace([float("inf"), -float("inf")], pd.NA)

# Round to 2 decimal places
df["SENSupportPercent"] = df["SENSupportPercent"].round(2)
df["EHCPPercent"] = df["EHCPPercent"].round(2)
df["InclusionBalance"] = df["InclusionBalance"].round(2)

# Save output
df.to_csv(output_path, index=False)
print(f"✅ School-level inclusion metrics saved to: {output_path}")