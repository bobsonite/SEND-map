import pandas as pd
import os

def split_urn_csv(input_csv='urn_list.csv', chunk_size=1000, output_dir='urn_chunks'):
    df = pd.read_csv(input_csv)
    urns = df.iloc[:, 0].tolist()  # assumes URNs are in the first column

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(0, len(urns), chunk_size):
        chunk = urns[i:i+chunk_size]
        chunk_df = pd.DataFrame(chunk, columns=['URN'])
        chunk_df.to_csv(f"{output_dir}/urn_chunk_{i//chunk_size + 1}.csv", index=False)
        print(f"✅ Saved chunk {i//chunk_size + 1} with {len(chunk)} URNs")

# Run this script once
split_urn_csv(input_csv='urn_list.csv', chunk_size=1000)