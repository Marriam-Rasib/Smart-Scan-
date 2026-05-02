import time
import requests
import json

API_KEY = "api_key"
ADDRESS_FILE = "addressesPolygon.txt"
OUTPUT_FILE = "PolygonContracts.json"
API_LINK = "https://api.polygonscan.com/api"

#function to read addresses
def get_contracts_address(file_path):
    with open(file_path, "r") as f:
        addresses = [line.strip() for line in f.readlines()]
    return addresses

#function to get Smart Contracts Data
def read_contracts_data(address):
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": API_KEY
    }
    response = requests.get(API_LINK, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for {address}: {response.status_code}")
        return None

#function to store data
def store_contracts_data(data, file_path):   
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def main():

    addresses = get_contracts_address(ADDRESS_FILE)
    contract_data = []

    print(f"Fetching data for {len(addresses)} contracts...")

    for i, address in enumerate(addresses):
        print(f"Fetching contract {i+1}/{len(addresses)}: {address}")
        data = read_contracts_data(address)

        if data:
            contract_data.append({
                "address": address,
                "source_code": data.get("result", [{}])[0].get("SourceCode", ""),
                "abi": data.get("result", [{}])[0].get("ABI", ""),
                "contract_name": data.get("result", [{}])[0].get("ContractName", ""),
                "compiler_version": data.get("result", [{}])[0].get("CompilerVersion", ""),
                "optimization_used": data.get("result", [{}])[0].get("OptimizationUsed", ""),
                "metadata": data.get("result", [{}])[0].get("Metadata", "")
            })

        # Respect API rate limit (5 requests per second)
        time.sleep(0.2)

    # Save fetched data to a file
    store_contracts_data(contract_data, OUTPUT_FILE)
    print(f"Contract data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

