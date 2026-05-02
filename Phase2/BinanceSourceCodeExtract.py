import requests
import json
import pandas as pd

API_KEY = "api_key"  
BASE_URL = "https://api.bscscan.com/api"

csv_file_path = 'verified-contract-address.csv'
data = pd.read_csv(csv_file_path, header=1)
contract_addresses = data.iloc[:, 1].tolist()  ## contract detailed are obtained from 2nd column of the csv file

print(f"Extracted {len(contract_addresses)} coacntract addresses.")

def fetch_contract_details(address):
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": API_KEY,
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for {address}: {e}")
        return None

## json data is stored in 2 files half each
contract_details_part1 = []
contract_details_part2 = []

for i, address in enumerate(contract_addresses[:3500]):
    try:
        details = fetch_contract_details(address)
        if details and details.get("status") == "1":  
            contract_data = details["result"][0]
            if i < 1750:  # First half
                contract_details_part1.append(contract_data)
            else:  # Second half
                contract_details_part2.append(contract_data)
            print(f"Fetched details for contract {i + 1}/{3500}")
    except Exception as e:
        print(f"Error processing contract at index {i}: {e}")


output_file_part1 = 'contract_details_part1.json'
with open(output_file_part1, 'w') as f:
    json.dump(contract_details_part1, f, indent=4)

print(f"First half of contract details saved to {output_file_part1}")


output_file_part2 = 'contract_details_part2.json'
with open(output_file_part2, 'w') as f:
    json.dump(contract_details_part2, f, indent=4)

print(f"Second half of contract details saved to {output_file_part2}")
