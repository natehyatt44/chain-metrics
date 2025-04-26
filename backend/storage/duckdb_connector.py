"""
DuckDB connection logic for reading/writing/querying analytics data.
"""

import duckdb
from typing import Optional
import polars as pl

def get_duckdb_connection(db_path: Optional[str] = None) -> duckdb.DuckDBPyConnection:
    """
    Returns a DuckDB connection. If db_path is None, uses in-memory DB.
    """
    return duckdb.connect(database=db_path or ':memory:') 