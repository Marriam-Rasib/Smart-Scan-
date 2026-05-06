import time
import requests
import json
import pandas as pd

API_KEY = "SCPTH137HA89YQWEVJ5NN8YSZ75ICRBZW2"
ADDRESS_FILE = "Contract Address polygon.csv"
OUTPUT_FILE = "PolygonContracts.json"
API_LINK = "https://api.etherscan.io/v2/api"

# =========================
# READ CSV CORRECTLY
# =========================
df = pd.read_csv(ADDRESS_FILE)

print(df.head())

# CHANGE COLUMN NAME IF NEEDED
addresses = df["ContractAddress"].dropna().tolist()

print(f"Total contracts: {len(addresses)}")

# =========================
# FETCH DATA
# =========================
def read_contracts_data(address):

    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "chainid": 137,   # Polygon mainnet
        "apikey": API_KEY
    }

    try:
        response = requests.get(API_LINK, params=params)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"Error for {address}: {e}")
        return None

# =========================
# MAIN
# =========================
contract_data = []

for i, address in enumerate(addresses):

    print(f"\nProcessing {i+1}/{len(addresses)}: {address}")

    data = read_contracts_data(address)

    if data and isinstance(data.get("result"), list):

        result = data["result"]

        if len(result) > 0 and isinstance(result[0], dict):

            r = result[0]

            contract_data.append({
                "address": address,
                "source_code": r.get("SourceCode", ""),
                "abi": r.get("ABI", ""),
                "contract_name": r.get("ContractName", ""),
                "compiler_version": r.get("CompilerVersion", ""),
                "optimization_used": r.get("OptimizationUsed", ""),
                "metadata": r.get("Metadata", "")
            })

        else:
            print("Invalid result format")

    else:
        print("Bad API response:", data)

    time.sleep(0.2)

# =========================
# SAVE OUTPUT
# =========================
with open(OUTPUT_FILE, "w") as f:
    json.dump(contract_data, f, indent=4)

print(f"\nSaved {len(contract_data)} contracts → {OUTPUT_FILE}")
