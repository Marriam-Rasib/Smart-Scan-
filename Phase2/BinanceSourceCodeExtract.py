# =========================================================
# Binance Smart Chain Contract Source Code Downloader
# =========================================================

import requests
import json
import pandas as pd
import time

# =========================================================
# API CONFIGURATION
# =========================================================

API_KEY = "SCPTH137HA89YQWEVJ5NN8YSZ75ICRBZW2"
BASE_URL = "https://api.bscscan.com/api"

# =========================================================
# LOAD CSV FILE
# =========================================================

csv_file_path = "verified-contract-address.csv"

# Read CSV
data = pd.read_csv(csv_file_path, header=1)

# Show first few rows for debugging
print("\nCSV Preview:")
print(data.head())

# =========================================================
# EXTRACT CONTRACT ADDRESSES
# =========================================================

# Change column index if needed
contract_addresses = data.iloc[:, 1].dropna().tolist()

print(f"\nExtracted {len(contract_addresses)} contract addresses.")

# =========================================================
# FUNCTION TO FETCH CONTRACT DETAILS
# =========================================================

def fetch_contract_details(address):

    params = {
        "chainid": 56,   # Binance Smart Chain
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": API_KEY,
    }

    try:

        response = requests.get(
            "https://api.etherscan.io/v2/api",
            params=params
        )

        response.raise_for_status()

        data = response.json()

        print(data)

        return data

    except requests.exceptions.RequestException as e:

        print(f"Error fetching details for {address}: {e}")

        return None
# =========================================================
# STORAGE LISTS
# =========================================================

contract_details_part1 = []
contract_details_part2 = []

# =========================================================
# FETCH CONTRACT DETAILS
# =========================================================

MAX_CONTRACTS = 100

for i, address in enumerate(contract_addresses[:MAX_CONTRACTS]):

    try:

        print(f"\nProcessing Contract {i+1}/{MAX_CONTRACTS}")
        print(f"Address: {address}")

        details = fetch_contract_details(address)

        # Check successful API response
        if details and details.get("status") == "1":

            contract_data = details["result"][0]

            # Store first half
            if i < MAX_CONTRACTS // 2:

                contract_details_part1.append(contract_data)

            # Store second half
            else:

                contract_details_part2.append(contract_data)

            print(f"Successfully fetched contract {i+1}")

        else:

            print(f"Failed API Response for {address}")
            print(details)

        # Delay to avoid rate limiting
        time.sleep(0.3)

    except Exception as e:

        print(f"Error processing contract at index {i}: {e}")

# =========================================================
# SAVE FIRST JSON FILE
# =========================================================

output_file_part1 = "contract_details_part1.json"

with open(output_file_part1, "w") as f:

    json.dump(contract_details_part1, f, indent=4)

print(f"\nFirst half saved to {output_file_part1}")

# =========================================================
# SAVE SECOND JSON FILE
# =========================================================

output_file_part2 = "contract_details_part2.json"

with open(output_file_part2, "w") as f:

    json.dump(contract_details_part2, f, indent=4)

print(f"Second half saved to {output_file_part2}")

# =========================================================
# FINAL SUMMARY
# =========================================================

print("\n================ FINAL SUMMARY ================")
print(f"Contracts saved in Part 1: {len(contract_details_part1)}")
print(f"Contracts saved in Part 2: {len(contract_details_part2)}")
print("Process Completed Successfully.")
