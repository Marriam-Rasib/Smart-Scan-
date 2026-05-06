# =========================================================
# Optimism Smart Contract Downloader (FIXED)
# =========================================================

import re
import time
import requests
import json
import csv

# =========================================================
# CONFIGURATION
# =========================================================

API_KEY      = "SCPTH137HA89YQWEVJ5NN8YSZ75ICRBZW2"
ADDRESS_FILE = "Contract Address Optimisim.csv"
OUTPUT_FILE  = "OptimismContracts2.json"
API_URL      = "https://api.etherscan.io/v2/api"
CHAIN_ID     = 10  # Optimism


# =========================================================
# ADDRESS VALIDATION
# =========================================================

def is_valid_address(addr: str) -> bool:
    """Valid EVM address: 0x + exactly 40 hex chars = 42 chars total."""
    return bool(re.fullmatch(r"0x[0-9a-fA-F]{40}", addr))


def clean_cell(raw: str) -> str:
    """Strip BOM, zero-width spaces, non-breaking spaces, surrounding quotes."""
    return (
        raw.strip()
           .strip('\ufeff')
           .strip('\u200b')
           .strip('\xa0')
           .strip('"')
           .strip("'")
           .strip()
    )


# =========================================================
# READ CONTRACT ADDRESSES
# =========================================================

def get_contract_addresses(file_path: str) -> list:
    """
    Reads ContractAddress from an Etherscan-exported CSV.

    Etherscan export format:
      Row 0  ->  Note: "For the actual contract source codes..."  (comment, skip)
      Row 1  ->  Header: Txhash, ContractAddress, ContractName
      Row 2+ ->  Data

    Txhash = 64-char hex  (transaction hash, NOT an address)
    ContractAddress = 40-char hex  (what we want)
    """
    addresses = []
    invalid   = []

    try:
        with open(file_path, newline="", encoding="utf-8-sig") as f:
            reader   = csv.reader(f)
            all_rows = [row for row in reader if any(c.strip() for c in row)]

        if not all_rows:
            print("Warning: CSV file is empty.")
            return []

        print(f"\nTotal rows in file: {len(all_rows)}")

        # ── Find the real header row (skip "Note:" comment rows)
        header_idx = None
        for i, row in enumerate(all_rows):
            first = clean_cell(row[0]) if row else ""
            if re.match(r'^[A-Za-z]', first) and not first.lower().startswith("note"):
                header_idx = i
                break

        if header_idx is None:
            header_idx = 0

        header    = [clean_cell(h).lower() for h in all_rows[header_idx]]
        data_rows = all_rows[header_idx + 1:]

        print(f"Header row : {header}")
        print(f"Data rows  : {len(data_rows)}")

        # ── Find ContractAddress column by name
        CANDIDATES = ("contractaddress", "contract_address", "address", "to")
        addr_col = None
        for candidate in CANDIDATES:
            if candidate in header:
                addr_col = header.index(candidate)
                break

        # ── Fallback: scan first data row for a 40-char address
        if addr_col is None and data_rows:
            for col_i, cell in enumerate(data_rows[0]):
                if is_valid_address(clean_cell(cell)):
                    addr_col = col_i
                    print(f"Warning: header name not matched, auto-detected address at column {col_i}")
                    break

        if addr_col is None:
            print("ERROR: Could not find ContractAddress column.")
            print(f"Header was: {header}")
            return []

        print(f"Using column '{header[addr_col]}' (index {addr_col})")

        # ── Extract and validate addresses
        skipped_tx = 0
        for i, row in enumerate(data_rows, 1):
            if addr_col >= len(row):
                continue
            addr = clean_cell(row[addr_col])
            if not addr:
                continue
            if is_valid_address(addr):
                addresses.append(addr)
            elif re.fullmatch(r"0x[0-9a-fA-F]{64}", addr):
                skipped_tx += 1  # tx hash in wrong column
            else:
                invalid.append((i, addr))

        if skipped_tx:
            print(f"\nWarning: {skipped_tx} tx hash(es) skipped (wrong column)")
        if invalid:
            print(f"Warning: {len(invalid)} unrecognised value(s) skipped")
            for row_num, val in invalid[:5]:
                print(f"  Row {row_num}: {repr(val)}")

        print(f"\nValid contract addresses loaded: {len(addresses)}")
        if addresses:
            print("Sample:")
            for a in addresses[:5]:
                print(f"  {a}")

        return addresses

    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        return []
    except Exception as e:
        print(f"ERROR reading file: {e}")
        return []


# =========================================================
# FETCH CONTRACT DATA
# =========================================================

def get_contract_data(address: str) -> dict | None:
    """Fetch verified source code from Etherscan V2 with retries."""
    params = {
        "chainid": CHAIN_ID,
        "module":  "contract",
        "action":  "getsourcecode",
        "address": address,
        "apikey":  API_KEY,
    }

    for attempt in range(1, 4):
        try:
            response = requests.get(API_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print(f"  Timeout (attempt {attempt}/3)")
        except requests.exceptions.RequestException as e:
            print(f"  Request error (attempt {attempt}/3): {e}")
        if attempt < 3:
            time.sleep(2)

    return None


# =========================================================
# SAVE DATA
# =========================================================

def store_data(data: list, file_path: str):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"\nSaved {len(data)} contract(s) -> {file_path}")


# =========================================================
# MAIN PROCESS
# =========================================================

def main():

    addresses = get_contract_addresses(ADDRESS_FILE)

    if not addresses:
        print("\nNo valid addresses to process. Check your CSV file.")
        return

    contract_data = []
    skipped       = []

    print(f"\n{'='*52}")
    print(f"  Processing {len(addresses)} contract(s) on Optimism")
    print(f"{'='*52}")

    for i, address in enumerate(addresses, 1):

        print(f"\n[{i:>4}/{len(addresses)}] {address}")

        data = get_contract_data(address)

        if data is None:
            print("  No response - skipped")
            skipped.append(address)
            continue

        status = data.get("status")
        result = data.get("result")

        if status != "1":
            print(f"  API error: {result}")
            skipped.append(address)

        elif isinstance(result, list) and result:
            r      = result[0]
            source = r.get("SourceCode", "")

            # Handle multi-file contracts (double-brace JSON wrapping)
            if isinstance(source, str) and source.startswith("{{"):
                try:
                    parsed = json.loads(source[1:-1])
                    source = "\n\n".join(
                        f"// === {fname} ===\n{fdata.get('content', '')}"
                        for fname, fdata in parsed.get("sources", {}).items()
                    )
                except json.JSONDecodeError:
                    pass

            name = r.get("ContractName", "Unknown")
            print(f"  OK: {name}  ({r.get('CompilerVersion', '?')})")

            contract_data.append({
                "address":           address,
                "contract_name":     name,
                "source_code":       source,
                "compiler_version":  r.get("CompilerVersion", ""),
                "optimization_used": r.get("OptimizationUsed", ""),
                "runs":              r.get("Runs") or r.get("OptimizationRuns", ""),
                "metadata":          r.get("Metadata", ""),
            })

        else:
            print(f"  Unexpected result: {result}")
            skipped.append(address)

        time.sleep(0.3)  # respect rate limit

        if i % 100 == 0:
            print("  Checkpoint save...")
            store_data(contract_data, OUTPUT_FILE)

    store_data(contract_data, OUTPUT_FILE)

    print(f"\n{'='*52}")
    print(f"  Done!")
    print(f"  Saved  : {len(contract_data)}")
    print(f"  Skipped: {len(skipped)}")
    if skipped:
        for s in skipped:
            print(f"    - {s}")
    print(f"{'='*52}")


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()
