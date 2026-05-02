import time
import requests
import json

API_KEY = "api_key"
ADDRESS_FILE = "optimismSecondHalf.txt"
OUTPUT_FILE = "OptimismContracts2.json"
API_URL = "https://api-optimistic.etherscan.io/api"

def get_contract_address(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]

def get_contract_data(address):
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": API_KEY
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting Contract {address}: HTTP {response.status_code}")
        return None

def store_data(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def main():
    # Read contract addresses from file
    addresses = get_contract_address(ADDRESS_FILE)
    contract_data = []

    print(f"Total contracts: {len(addresses)}")

    for i, address in enumerate(addresses):
        print(f"Getting contract {i + 1}/{len(addresses)}: {address}")
        data = get_contract_data(address)

        if data and data.get("result"):
            result = data["result"][0]
            contract_data.append({
                "address": address,
                "source_code": result.get("SourceCode", ""),
                "compiler_version": result.get("CompilerVersion", ""),
                "optimization_used": result.get("OptimizationUsed", ""),
                "contract_name": result.get("ContractName", ""),
                "metadata": result.get("Metadata", "")
            })
        else:
            print(f" {address}: has valid data received.")

        time.sleep(0.2)

        if (i + 1) % 100 == 0:
            print(f"Saving {i + 1} contracts...")
            store_data(contract_data, OUTPUT_FILE)

    store_data(contract_data, OUTPUT_FILE)
    print(f"Data collected. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

