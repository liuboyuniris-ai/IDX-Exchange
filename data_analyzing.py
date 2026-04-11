# import pandas as pd
# df=pd.read_csv("CRMLSListing2024-2026_Concat.csv")
# df.info()
# df.isnull().sum()
import pandas as pd
import numpy as np

# 1. Load data
# Make sure the file name matches your local file
file_path = 'CRMLSSold2024-2026_Concat.csv'
print(f"Loading data: {file_path}...")
df = pd.read_csv(file_path, low_memory=False)

# 2. Basic dataset information (Dataset Understanding)
print("\n--- 1. Basic Dataset Information ---")
rows, cols = df.shape
print(f"Number of rows: {rows}")
print(f"Number of columns: {cols}")
print("\nSummary of column data types:")
print(df.dtypes.value_counts())

# 3. Property type check and filtering (Property Type Filtering)
print("\n--- 2. Property Type Check ---")
unique_types = df['PropertyType'].unique()
print(f"Discovered property types: {unique_types}")

# Keep only Residential
initial_count = len(df)
df_res = df[df['PropertyType'] == 'Residential'].copy()
filtered_count = len(df_res)
print(f"Filtering complete: reduced from {initial_count} rows to {filtered_count} rows (Residential only)")

# 4. Missing value analysis (Missing Value Analysis)
print("\n--- 3. Missing Value Report ---")
null_counts = df_res.isnull().sum()
null_percentages = (null_counts / len(df_res)) * 100

missing_report = pd.DataFrame({
    'Column': df_res.columns,
    'Missing Count': null_counts,
    'Percentage (%)': null_percentages
})

# Flag columns with missing rate > 90%
high_missing_cols = missing_report[missing_report['Percentage (%)'] > 90]
print("Columns with more than 90% missing values:")
print(high_missing_cols[['Column', 'Percentage (%)']])

# 5. Core numeric field distribution summary (Numeric Distribution Review)
print("\n--- 4. Core Numeric Distribution Summary ---")
core_numeric_fields = ['ClosePrice', 'LivingArea', 'DaysOnMarket']

# Ensure these columns are numeric
for field in core_numeric_fields:
    df_res[field] = pd.to_numeric(df_res[field], errors='coerce')

# Generate summary table (min, max, mean, median, percentiles)
dist_summary = df_res[core_numeric_fields].describe(percentiles=[.25, .5, .75, .9])
print(dist_summary)

# 6. Logical validation (Validation)
print("\n--- 5. Data Logical Validation ---")
# Check if CloseDate is earlier than ListingContractDate (convert to datetime first)
df_res['CloseDate'] = pd.to_datetime(df_res['CloseDate'], errors='coerce')
df_res['ListingContractDate'] = pd.to_datetime(df_res['ListingContractDate'], errors='coerce')

date_issues = df_res[df_res['CloseDate'] < df_res['ListingContractDate']]
print(f"Number of date logic issues (closing before listing): {len(date_issues)}")

# 7. Save results
print("\n--- 6. Save Filtered Dataset ---")
output_file = 'CRMLSSold_Residential_Filtered.csv'
df_res.to_csv(output_file, index=False)
print(f"Filtered dataset saved as: {output_file}")

# 8. Additional task: median house price by county
if 'CountyOrParish' in df_res.columns:
    print("\nTop 5 counties by median closing price:")
    print(df_res.groupby('CountyOrParish')['ClosePrice'].median().sort_values(ascending=False).head(5))