import csv
import requests
from datetime import datetime

# 1. API Configuration
url_base = 'https://api-trestle.corelogic.com/trestle/odata/Property'
auth_endpoint = 'https://idxexchange.com/internal-api/trestle_token.php?key=IDXEXCHANGE2026_CHANGE_THIS'

# 2. Get Access Token
print("Requesting access token...")
try:
    response = requests.get(auth_endpoint, timeout=30)
    response.raise_for_status()
    token = response.json().get('access_token')
except Exception as e:
    print(f"Auth Error: {e}")
    exit()

if not token:
    print("Error: access_token not found in response")
    exit()

headers = {'Authorization': f'Bearer {token}'}

# 3. Define Fields
field_list = [
    'OriginalListPrice', 'ListingKey', 'CloseDate', 'ClosePrice', 'ListAgentFirstName', 
    'ListAgentLastName', 'Latitude', 'Longitude', 'UnparsedAddress', 'PropertyType', 
    'LivingArea', 'ListPrice', 'DaysOnMarket', 'ListOfficeName', 'BuyerOfficeName', 
    'CoListOfficeName', 'ListAgentFullName', 'CoListAgentFirstName', 'CoListAgentLastName', 
    'BuyerAgentMlsId', 'BuyerAgentFirstName', 'BuyerAgentLastName', 'FireplacesTotal', 
    'AssociationFeeFrequency', 'AboveGradeFinishedArea', 'ListingKeyNumeric', 'MLSAreaMajor', 
    'TaxAnnualAmount', 'CountyOrParish', 'MlsStatus', 'ElementarySchool', 'AttachedGarageYN', 
    'ParkingTotal', 'BuilderName', 'PropertySubType', 'LotSizeAcres', 'SubdivisionName', 
    'BuyerOfficeAOR', 'YearBuilt', 'StreetNumberNumeric', 'ListingId', 'BathroomsTotalInteger', 
    'City', 'TaxYear', 'BuildingAreaTotal', 'BedroomsTotal', 'ContractStatusChangeDate', 
    'ElementarySchoolDistrict', 'CoBuyerAgentFirstName', 'PurchaseContractDate', 
    'ListingContractDate', 'BelowGradeFinishedArea', 'BusinessType', 'StateOrProvince', 
    'CoveredSpaces', 'MiddleOrJuniorSchool', 'FireplaceYN', 'Stories', 'HighSchool', 
    'Levels', 'LotSizeDimensions', 'LotSizeArea', 'MainLevelBedrooms', 'NewConstructionYN', 
    'GarageSpaces', 'HighSchoolDistrict', 'PostalCode', 'AssociationFee', 'LotSizeSquareFeet', 
    'MiddleOrJuniorSchoolDistrict'
]

# 4. Double Loop for 2024 and 2025
years = [2024, 2025]
grand_total = 0 # 统计所有月份的总记录数

for year in years:
    for month in range(1, 13):
        current_url = url_base # 每次循环重置当前请求的 URL
        
        # Calculate Date Range
        start_dt = datetime(year, month, 1)
        if month == 12:
            end_dt = datetime(year + 1, 1, 1)
        else:
            end_dt = datetime(year, month + 1, 1)

        # API Parameters
        params = {
            '$select': ','.join(field_list),
            '$filter': f"ListingContractDate ge {start_dt.isoformat(timespec='milliseconds')}Z and ListingContractDate lt {end_dt.isoformat(timespec='milliseconds')}Z",
            '$top': 1000  
        }

        # Dynamic Filename
        csv_file = f'CRMLSListing{year}{month:02d}.csv'
        month_records = 0 # 统计当月记录数
        print(f"--- Fetching: {year}-{month:02d} -> {csv_file} ---")

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
                            # 写入数据
                            writer.writerow({field: obs.get(field, '') for field in field_list})
                            month_records += 1
                            grand_total += 1

                        # Pagination check
                        if '@odata.nextLink' in data:
                            current_url = data['@odata.nextLink']
                            params = None # 使用 nextLink 时不需要重复传 params
                        else:
                            break
                    else:
                        print(f"API Error ({response.status_code}) at {year}-{month:02d}: {response.text}")
                        break
                except Exception as e:
                    print(f"Connection Error at {year}-{month:02d}: {e}")
                    break

        print(f"Successfully exported {month_records} records for {year}-{month:02d}")

print(f"\nMission Accomplished! Total {grand_total} records downloaded across 24 months.")