import csv
import requests
from datetime import datetime

# 1. API Configuration
url_base = 'https://api-trestle.corelogic.com/trestle/odata/Property'
auth_endpoint = 'https://idxexchange.com/internal-api/trestle_token.php?key=IDXEXCHANGE2026_CHANGE_THIS'

# 2. Get Access Token
print("Requesting access token for Sold data...")
try:
    response = requests.get(auth_endpoint, timeout=30)
    response.raise_for_status()
    token = response.json().get('access_token')
except Exception as e:
    print(f"Auth Error: {e}")
    exit()

if not token:
    print("Error: access_token not found")
    exit()

headers = {'Authorization': f'Bearer {token}'}

# 3. Define the full list of fields from your script
field_list = [
    'BuyerAgentAOR', 'ListAgentAOR', 'Flooring', 'ViewYN', 'WaterfrontYN', 'BasementYN', 
    'PoolPrivateYN', 'OriginalListPrice', 'ListingKey', 'CloseDate', 'ClosePrice', 
    'ListAgentFirstName', 'ListAgentLastName', 'Latitude', 'Longitude', 'UnparsedAddress', 
    'PropertyType', 'LivingArea', 'ListPrice', 'DaysOnMarket', 'ListOfficeName', 
    'BuyerOfficeName', 'CoListOfficeName', 'ListAgentFullName', 'CoListAgentFirstName', 
    'CoListAgentLastName', 'BuyerAgentMlsId', 'BuyerAgentFirstName', 'BuyerAgentLastName', 
    'FireplacesTotal', 'AssociationFeeFrequency', 'AboveGradeFinishedArea', 'ListingKeyNumeric', 
    'MLSAreaMajor', 'TaxAnnualAmount', 'CountyOrParish', 'MlsStatus', 'ElementarySchool', 
    'AttachedGarageYN', 'ParkingTotal', 'BuilderName', 'PropertySubType', 'LotSizeAcres', 
    'SubdivisionName', 'YearBuilt', 'StreetNumberNumeric', 'ListingId', 'BathroomsTotalInteger', 
    'City', 'TaxYear', 'BuildingAreaTotal', 'BedroomsTotal', 'ContractStatusChangeDate', 
    'ElementarySchoolDistrict', 'CoBuyerAgentFirstName', 'PurchaseContractDate', 
    'ListingContractDate', 'BelowGradeFinishedArea', 'BusinessType', 'StateOrProvince', 
    'CoveredSpaces', 'MiddleOrJuniorSchool', 'FireplaceYN', 'Stories', 'HighSchool', 
    'Levels', 'LotSizeDimensions', 'LotSizeArea', 'MainLevelBedrooms', 'NewConstructionYN', 
    'GarageSpaces', 'HighSchoolDistrict', 'PostalCode', 'AssociationFee', 'LotSizeSquareFeet', 
    'MiddleOrJuniorSchoolDistrict', 'OriginatingSystemName', 'OriginatingSystemSubName'
]

# 4. Double Loop for 2024 and 2025
years = [2024, 2025]
grand_total = 0

for year in years:
    for month in range(1, 13):
        current_url = url_base
        
        # Calculate Date Range for each month
        start_dt = datetime(year, month, 1)
        if month == 12:
            end_dt = datetime(year + 1, 1, 1)
        else:
            end_dt = datetime(year, month + 1, 1)

        # Define API Parameters
        params = {
            '$select': ','.join(field_list),
            # Note: We filter by CloseDate for Sold data as per your script
            '$filter': f"MlsStatus eq 'Closed' and CloseDate ge {start_dt.isoformat(timespec='milliseconds')}Z and CloseDate lt {end_dt.isoformat(timespec='milliseconds')}Z",
            '$top': 1000  
        }

        csv_file = f'CRMLSSold{year}{month:02d}.csv'
        month_records = 0
        print(f"--- Fetching Sold Data: {year}-{month:02d} -> {csv_file} ---")

        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=field_list)
            writer.writeheader()

            while True:
                try:
                    response = requests.get(current_url, params=params, headers=headers, timeout=60)
                    if response.status_code == 200:
                        data = response.json()
                        observations = data.get('value', [])
                        
                        for obs in observations:
                            # Automatically map observations to fields
                            writer.writerow({field: obs.get(field, '') for field in field_list})
                            month_records += 1
                            grand_total += 1

                        if '@odata.nextLink' in data:
                            current_url = data['@odata.nextLink']
                            params = None
                        else:
                            break
                    else:
                        print(f"API Error ({response.status_code}) at {year}-{month:02d}: {response.text}")
                        break
                except Exception as e:
                    print(f"Connection Error at {year}-{month:02d}: {e}")
                    break

        print(f"Completed {year}-{month:02d}: {month_records} records.")

print(f"\nAll Sold data (2024-2025) downloaded! Grand total: {grand_total} records.")