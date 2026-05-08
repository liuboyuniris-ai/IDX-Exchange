import pandas as pd
import numpy as np

# 1. Load the Enriched Dataset
print("Loading enriched dataset...")
file_path = 'CRMLSSold_Enriched.csv'
df = pd.read_csv(file_path, low_memory=False)
initial_row_count = len(df)

# 2. Convert Date Fields to Datetime Format
# Ensuring all time-related columns are standardized for calculation
print("Converting date fields...")
date_cols = [
    'CloseDate', 
    'PurchaseContractDate', 
    'ListingContractDate', 
    'ContractStatusChangeDate'
]
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# 3. Numeric Data Cleaning (The "Mask" Filtering)
# We use boolean indexing to filter out physically impossible or invalid records
print("Applying numeric data filters...")
mask = (
    (df['ClosePrice'] > 0) & 
    (df['LivingArea'] > 0) & 
    (df['DaysOnMarket'] >= 0) & 
    (df['BedroomsTotal'] >= 0) & 
    (df['BathroomsTotalInteger'] >= 0)
)

# Apply the filter and keep a copy
df_clean = df[mask].copy()
after_numeric_count = len(df_clean)

# 4. Date Consistency Checks (Flagging Logical Errors)
# Create boolean flags for records that violate chronological order
print("Performing date consistency checks...")

# Flag: Listing happens after the sale is already closed
df_clean['listing_after_close_flag'] = df_clean['ListingContractDate'] >= df_clean['CloseDate']

# Flag: Contract is signed after the sale is already closed
df_clean['purchase_after_close_flag'] = df_clean['PurchaseContractDate'] >= df_clean['CloseDate']

# Flag: Any timeline violation (Listing > Purchase OR Purchase > Close)
df_clean['negative_timeline_flag'] = (
    (df_clean['ListingContractDate'] >= df_clean['PurchaseContractDate']) | 
    (df_clean['PurchaseContractDate'] >= df_clean['CloseDate'])
)

# 5. Geographic Data Quality Checks (California Specific)
print("Validating geographic coordinates...")
# Longitude must be negative for California (West of Prime Meridian)
# Latitude/Longitude should not be null or exactly 0 (sentinel values)
df_clean['invalid_coords_flag'] = (
    df_clean['Latitude'].isnull() | 
    df_clean['Longitude'].isnull() | 
    (df_clean['Latitude'] == 0) | 
    (df_clean['Longitude'] >= 0)
)

# 6. Generate Data Quality Summary Report
print("\n" + "="*40)
print("DATA CLEANING & PREPARATION SUMMARY")
print("="*40)
print(f"Initial row count:             {initial_row_count}")
print(f"Rows after numeric filtering:  {after_numeric_count}")
print(f"Rows removed (invalid data):   {initial_row_count - after_numeric_count}")
print("-" * 40)
print(f"Date Timeline Conflicts:       {df_clean['negative_timeline_flag'].sum()}")
print(f"Invalid Geographic Coords:     {df_clean['invalid_coords_flag'].sum()}")
print("="*40)

# 7. Verify Data Types for Deliverable
print("\nData Type Confirmation:")
print(df_clean[date_cols].dtypes)

# 8. Save the Final Analysis-Ready Dataset
output_file = 'CRMLSSold_Final_Cleaned.csv'
df_clean.to_csv(output_file, index=False)
print(f"\nSuccess! Cleaned dataset saved as: {output_file}")