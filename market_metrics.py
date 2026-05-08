import pandas as pd

# 1. Load the Cleaned Dataset
print("Loading cleaned dataset...")
df = pd.read_csv('CRMLSSold_Final_Cleaned.csv', low_memory=False)

# Ensure date formats are correct
date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate']
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# 2. Feature Engineering: Creating Market Metrics
print("Engineering market metrics...")

# A. Price Metrics
df['PricePerSqFt'] = df['ClosePrice'] / df['LivingArea']
df['CloseToOriginalListRatio'] = df['ClosePrice'] / df['OriginalListPrice']

# B. Time-Series Metrics
# Create Year-Month for time-series (e.g., 2024-05)
df['YrMo'] = df['CloseDate'].dt.to_period('M')
df['Year'] = df['CloseDate'].dt.year
df['Month'] = df['CloseDate'].dt.month

# C. Timeline Duration Metrics (Calculated in Days)
# Note: .dt.days converts timedelta objects to simple integers
df['Days_ListingToContract'] = (df['PurchaseContractDate'] - df['ListingContractDate']).dt.days
df['Days_ContractToClose'] = (df['CloseDate'] - df['PurchaseContractDate']).dt.days

# 3. Handling Outliers in new metrics (Optional but professional)
# If some ratios are infinity or negative due to bad data, we cap them
df = df.replace([float('inf'), -float('inf')], 0)

# 4. Segment Analysis: Summary Statistics
print("\n--- Market Segment Summary (By County) ---")
county_summary = df.groupby('CountyOrParish').agg({
    'ClosePrice': 'median',
    'PricePerSqFt': 'mean',
    'CloseToOriginalListRatio': 'mean',
    'DaysOnMarket': 'median',
    'Days_ContractToClose': 'mean'
}).rename(columns={'ClosePrice': 'Median_ClosePrice'}).sort_values('Median_ClosePrice', ascending=False)

print(county_summary.head(10))

# Additional Segment Analysis: Summary by PropertyType
print("\n--- Market Segment Summary (By PropertyType) ---")
property_summary = df.groupby('PropertyType').agg({
    'ClosePrice': ['median', 'mean', 'count'],
    'PricePerSqFt': 'mean',
    'CloseToOriginalListRatio': 'mean',
    'DaysOnMarket': 'median',
    'Days_ListingToContract': 'mean',
    'Days_ContractToClose': 'mean'
}).rename(columns={'ClosePrice': 'Median_ClosePrice'}).sort_values(('Median_ClosePrice', 'median'), ascending=False)

print(property_summary.head(10))

# Optional: Summary by MLSAreaMajor for additional insights
print("\n--- Market Segment Summary (By MLSAreaMajor) ---")
area_summary = df.groupby('MLSAreaMajor').agg({
    'ClosePrice': 'median',
    'PricePerSqFt': 'mean',
    'CloseToOriginalListRatio': 'mean'
}).sort_values('ClosePrice', ascending=False)

print(area_summary.head(10))

# 5. Preview New Columns (For Deliverable)
print("\n--- Engineered Features Preview ---")
cols_to_show = ['ClosePrice', 'OriginalListPrice', 'PricePerSqFt', 'CloseToOriginalListRatio', 'YrMo', 'Days_ListingToContract', 'Days_ContractToClose']
print(df[cols_to_show].head())

# 6. Save the Enriched Dataset
output_file = 'CRMLSSold_Market_Metrics.csv'
df.to_csv(output_file, index=False)
print(f"\nSuccess! Market metrics dataset saved as: {output_file}")