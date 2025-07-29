import pandas as pd
from pathlib import Path

# === 1. Load workbook ===
file_path = Path.home() / "Documents" / "SEND-map" / "data" / "raw" / "NewAttainment.xlsx"
sheets = pd.read_excel(file_path, sheet_name=None)

# === 2. Normalize URNs ===
for name in sheets:
    if "URN" in sheets[name].columns:
        sheets[name]["URN"] = (
            pd.to_numeric(sheets[name]["URN"], errors="coerce")
            .fillna(0)
            .astype(int)
            .astype(str)
        )

# === 3. Clean SUPP and convert columns ===
def clean_sheet(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = df[col].replace("SUPP", pd.NA)
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

sheets["KS4_Destinations"] = clean_sheet(
    sheets["KS4_Destinations"],
    ["KS4_EAE_%", "KS4_EAE_Disadv_%", "KS4_EAE_NonDisadv_%"]
)

sheets["KS5_Destinations"] = clean_sheet(
    sheets["KS5_Destinations"],
    [
        "KS5_EAE_%", "KS5_Apprenticeship_%", "KS5_Education_%", "KS5_Work_%",
        "KS5_Not_Sustained_%", "% of disadvantaged students sustaining EAE",
        "% of non-disadvantaged in EAE"
    ]
)

sheets["HE_Progression"] = clean_sheet(
    sheets["HE_Progression"],
    ["HE_TopThird_%_All", "HE_HigherTech_%_All", "HE_Progression_%_Disadv"]
)

# === 4. Build master list of all unique URNs ===
all_urns = pd.concat([df[["URN"]] for df in sheets.values() if "URN" in df.columns]).drop_duplicates()

# === 5. Start with master URN table ===
df_merged = all_urns.copy()
overlap_log = {}

# === 6. Merge each sheet using outer join on URN ===
for name, df in sheets.items():
    df = df.drop_duplicates(subset="URN")  # avoid explosion from duplicate URNs
    overlaps = set(df_merged.columns).intersection(set(df.columns)) - {"URN"}
    overlap_log[name] = sorted(list(overlaps))
    df_merged = df_merged.merge(df, on="URN", how="left", suffixes=("", f"_{name}"))

# === 7. Export safely ===
output_path = Path.home() / "Documents" / "SEND-map" / "data" / "raw" / "Attainment_Merged.xlsx"
df_merged.to_excel(output_path, index=False)

# === 8. Overlap audit ===
print(f"\n✅ Merged file saved to: {output_path}\n")
print("=== Overlapping Columns Log ===")
for sheet, cols in overlap_log.items():
    if cols:
        print(f"{sheet}: {cols}")
    else:
        print(f"{sheet}: (no overlaps)")