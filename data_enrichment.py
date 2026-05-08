import pandas as pd

# Step 1: Load combined MLS datasets
print("Loading local MLS datasets...")
sold = pd.read_csv('CRMLSSold2024-2026_Concat.csv', low_memory=False)
listings = pd.read_csv('CRMLSListing2024-2026_Concat.csv', low_memory=False)

# Step 2: Fetch mortgage rate data from FRED 
print("Fetching live mortgage rates from FRED (St. Louis Fed)...")
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

# Step 3: Resample weekly rates to monthly averages
# Convert specific dates to a 'Year-Month' period
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)
print("Mortgage data successfully resampled to monthly averages.")

# Step 4: Create matching year_month keys on the MLS datasets 
# For Sold data: Key off the CloseDate (Completion of sale)
sold['year_month'] = pd.to_datetime(sold['CloseDate'], errors='coerce').dt.to_period('M')

# For Listings data: Key off the ListingContractDate (Start of listing)
listings['year_month'] = pd.to_datetime(listings['ListingContractDate'], errors='coerce').dt.to_period('M')

# Step 5: Merge (Left Join) mortgage rates onto MLS datasets
# We use a left join to keep all MLS records and attach the rate corresponding to that month
sold_enriched = sold.merge(mortgage_monthly, on='year_month', how='left')
listings_enriched = listings.merge(mortgage_monthly, on='year_month', how='left')

#Step 6:Check for nulls ensures every transaction was matched with a mortgage rate
null_sold = sold_enriched['rate_30yr_fixed'].isnull().sum()
null_listings = listings_enriched['rate_30yr_fixed'].isnull().sum()
print(null_sold)
print(null_listings)

#Step 7: Save the enriched datasets
# (These files will be large, remember to keep them in .gitignore)
sold_enriched.to_csv('CRMLSSold_Enriched.csv', index=False)
listings_enriched.to_csv('CRMLSListing_Enriched.csv', index=False)
print("Success! Enriched datasets saved as new CSV files.")