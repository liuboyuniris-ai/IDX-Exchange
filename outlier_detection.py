import pandas as pd

# 1. Load the Dataset
print("Loading dataset...")
df = pd.read_csv('CRMLSSold_Market_Metrics.csv', low_memory=False)

# Ensure date formats are correct (if needed)
date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate']
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# 2. Outlier Detection Function using IQR
def detect_outliers_iqr(df, column, multiplier=1.5):
    """
    Detect outliers using Interquartile Range (IQR) method.
    Returns lower and upper bounds, and a flag series.
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    outlier_flag = (df[column] < lower_bound) | (df[column] > upper_bound)
    return lower_bound, upper_bound, outlier_flag

# 3. Apply Outlier Detection to Key Fields
print("Detecting outliers...")

# Key fields for outlier detection
key_fields = ['ClosePrice', 'LivingArea', 'DaysOnMarket']

# Initialize outlier flag columns
for field in key_fields:
    _, _, df[f'{field}_Outlier'] = detect_outliers_iqr(df, field)

# Overall outlier flag: True if any key field is an outlier
df['Is_Outlier'] = df[[f'{field}_Outlier' for field in key_fields]].any(axis=1)

# 4. Business Rules: Additional Filtering
# Remove records where ClosePrice <= 0 (always invalid)
df = df[df['ClosePrice'] > 0]

# 5. Create Filtered Dataset (Remove Outliers)
df_filtered = df[~df['Is_Outlier']].copy()

# 6. Comparison: Dataset Size and Median Values
print("\n--- Dataset Comparison ---")
print(f"Original dataset size: {len(df)} records")
print(f"Filtered dataset size: {len(df_filtered)} records")
print(f"Records removed: {len(df) - len(df_filtered)} ({(len(df) - len(df_filtered)) / len(df) * 100:.2f}%)")

print("\nMedian values comparison:")
for field in key_fields:
    original_median = df[field].median()
    filtered_median = df_filtered[field].median()
    print(f"{field}: Original = {original_median:.2f}, Filtered = {filtered_median:.2f}")

# 7. Save Datasets
# Full flagged dataset
flagged_file = 'CRMLSSold_Flagged_Outliers.csv'
df.to_csv(flagged_file, index=False)
print(f"\nFlagged dataset saved as: {flagged_file}")

# Clean filtered dataset
filtered_file = 'CRMLSSold_Clean_Filtered.csv'
df_filtered.to_csv(filtered_file, index=False)
print(f"Clean filtered dataset saved as: {filtered_file}")

print("\nOutlier detection and filtering complete!")