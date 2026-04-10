import pandas as pd
import glob

# 1. Identify all the CSV files matching your naming pattern
# glob.glob finds all files starting with "CRMLSSold2026"
all_files = sorted(glob.glob("CRMLSSold*.csv"))

print(f"Files found for merging: {all_files}")

# 2. Read all files into a list and concatenate them
# ignore_index=True ensures the final dataframe has a clean, continuous index
combined_df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)

# 3. Save the merged result into a single large CSV
output_file = "CRMLSSold2024-2026_Concat.csv"
combined_df.to_csv(output_file, index=False)

print(f"--- Success! Total records merged: {len(combined_df)} ---")
print(f"Final file saved as: {output_file}")