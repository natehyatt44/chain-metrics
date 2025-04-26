# Chain Metrics for Hedera Hashgraph

A modular analytics platform for Hedera Hashgraph, starting with data collection and time-series metrics. 

## Project Structure

```
chain-metrics-app/
├── backend/
│   ├── ingest/
│   │   └── hedera_ingest.py          # Pulls data from mirror node or SDK
│   ├── models/
│   │   └── metric_engine.py          # Polars + DuckDB models/metrics
│   ├── api/
│   │   └── main.py                   # FastAPI app exposing metrics
│   ├── storage/
│   │   └── duckdb_connector.py       # DuckDB logic (read/write/query)
│   ├── utils/
│   │   └── time_helpers.py           # Handy timestamp converters, etc.
│   └── requirements.txt
├── data/
│   └── hedera_txn.parquet            # Sample data files (or local DuckDB file)
├── frontend/
│   └── (React/Vite/Tailwind App)     # Fully separate, API-driven UI
└── README.md
```

## Quickstart: Ingest Hedera Transactions

1. **Install dependencies**

```bash
cd backend
pip install -r requirements.txt
```

2. **Run the ingestion script**

```bash
python ingest/hedera_ingest.py
```

This will fetch recent transactions from the Hedera Mirror Node and save them as a Parquet file in `data/hedera_txn.parquet`.

---

- Modular, testable, and ready for extension to contracts, tokens, and more.
- Uses Polars for fast analytics and Parquet for efficient storage. 