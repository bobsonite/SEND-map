import pandas as pd

# Load the CSV
file_path = '/Users/saaj/Documents/SEND-map/data/raw/LA_ExcSus_final.csv'  # UPDATE this if needed
df = pd.read_csv(file_path)

# Clean column names
df.columns = df.columns.str.strip()

# Define the relevant columns
region_col = 'region_name'
headcount_col = 'Total_SEND Headcount'
send_one_plus_col = 'SEND one_plus_susp rate'
send_excl_col = 'SEND exclusion rate'

# Calculate weighted averages per region
region_stats = df.groupby(region_col).apply(
    lambda x: pd.Series({
        'weighted_one_plus': (x[send_one_plus_col] * x[headcount_col]).sum() / x[headcount_col].sum(),
        'weighted_exclusion': (x[send_excl_col] * x[headcount_col]).sum() / x[headcount_col].sum()
    })
).reset_index()

# Merge results back into original dataframe
df = df.merge(region_stats, on=region_col, how='left')

# Fill Column U and X (in-place)
df['Weighted Region SEND one plus rate'] = df['weighted_one_plus']
df['Weighted Region SEND exclusion rate'] = df['weighted_exclusion']

# Drop helper columns
df.drop(['weighted_one_plus', 'weighted_exclusion'], axis=1, inplace=True)

# Save the enriched file
output_path = '/Users/yourusername/Documents/SEND-map/data/raw/LA_ExcSus_final_enriched.csv'  # UPDATE this if needed
df.to_csv(output_path, index=False)

print("✅ Saved enriched file to:", output_path)
