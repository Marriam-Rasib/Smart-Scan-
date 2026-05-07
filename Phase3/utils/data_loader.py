import json


def safe_load_json(filepath):

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        print(f"Loaded {len(data)} contracts from {filepath}")

        return data

    except Exception as e:

        print(f"\nERROR loading {filepath}")
        print(e)

        return []


def load_all_contracts(files):

    all_contracts = []

    for file in files:

        contracts = safe_load_json(file)

        all_contracts.extend(contracts)

    print(f"\nTotal contracts loaded: {len(all_contracts)}")

    return all_contracts
