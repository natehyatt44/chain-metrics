import requests
import polars as pl
from typing import List, Dict, Any, Optional
import logging
import duckdb
import time
import pprint
from datetime import datetime
import json

HEDERA_MIRROR_API = "https://mainnet-public.mirrornode.hedera.com/api/v1"
TXN_ENDPOINT = "/transactions"
PAGE_SIZE = 100
DEFAULT_START_TIMESTAMP = "1745634000.000000000"  # 2025-06-01T00:00:00Z

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def timestamp_to_utc(ts: str) -> str:
    """Convert Hedera consensus timestamp string to UTC ISO8601."""
    seconds = int(float(ts))
    return datetime.utcfromtimestamp(seconds).isoformat() + "Z"

def fetch_transactions_paginated(
    start_timestamp: str,
    limit: int = PAGE_SIZE,
    max_pages: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Fetches Hedera transactions from the Mirror Node API starting from a given timestamp.
    Paginates through all available results.
    """
    url = f"{HEDERA_MIRROR_API}{TXN_ENDPOINT}?timestamp=gt:{start_timestamp}&limit={limit}&order=asc"
    all_txns = []
    page_count = 0

    while url:
        logger.info(f"Fetching: {url}")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        txns = data.get("transactions", [])
        all_txns.extend(txns)
        next_url = data.get("links", {}).get("next")
        if next_url:
            if next_url.startswith("http"):
                url = next_url
            elif next_url.startswith("/api/v1"):
                # Only prepend the domain, not the full base URL
                url = "https://mainnet-public.mirrornode.hedera.com" + next_url
            else:
                url = HEDERA_MIRROR_API + next_url
        else:
            url = None
        page_count += 1
        if max_pages and page_count >= max_pages:
            break
        # Optional: sleep to avoid rate limits
        time.sleep(0.1)
    return all_txns

def normalize_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ensures all dicts have the same keys and flattens nested fields as JSON strings.
    """
    # Find all keys
    all_keys = set()
    for tx in transactions:
        all_keys.update(tx.keys())
    # Normalize and flatten
    normalized = []
    for tx in transactions:
        row = {}
        for key in all_keys:
            value = tx.get(key, None)
            # If value is a list or dict, store as JSON string
            if isinstance(value, (list, dict)):
                row[key] = json.dumps(value)
            else:
                row[key] = value
        normalized.append(row)
    return normalized

def transactions_to_df(transactions: List[Dict[str, Any]]) -> pl.DataFrame:
    """
    Converts a list of transaction dicts to a Polars DataFrame, normalizing nested fields.
    """
    if not transactions:
        return pl.DataFrame()
    normalized = normalize_transactions(transactions)
    return pl.DataFrame(normalized)

def save_to_duckdb_incremental(df: pl.DataFrame, db_path: str, table_name: str = "hedera_txn") -> None:
    con = duckdb.connect(db_path)
    con.register("temp_df", df)
    # Create table if it doesn't exist
    con.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM temp_df WHERE FALSE"
    )
    # Insert new data
    con.execute(f"INSERT INTO {table_name} SELECT * FROM temp_df")
    con.unregister("temp_df")
    con.close()

def main():
    start_timestamp = DEFAULT_START_TIMESTAMP  # Or get from CLI/env/config
    txns = fetch_transactions_paginated(start_timestamp)
    df = transactions_to_df(txns)
    save_to_duckdb_incremental(df, "../data/chain_metrics.duckdb")

    # Print 5 sample rows
    con = duckdb.connect("../data/chain_metrics.duckdb")
    pl_df: pl.DataFrame = con.execute("SELECT * FROM hedera_txn LIMIT 5").pl()
    for row in pl_df.rows(named=True):
        pprint.pprint(row)
        print('-' * 40)
    con.close()

if __name__ == "__main__":
    main()

print("DEFAULT_START_TIMESTAMP =",
      DEFAULT_START_TIMESTAMP,
      "->",
      timestamp_to_utc(DEFAULT_START_TIMESTAMP)) 