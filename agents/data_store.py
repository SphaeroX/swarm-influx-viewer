"""Utility module to cache query results on disk."""

import json
import os

cached_data = None
CACHE_FILE = os.getenv("CACHE_FILE", "cached_data.json")


def store_cached_data(data) -> str:
    """Persist data to ``CACHE_FILE`` and update the in-memory cache."""
    global cached_data
    cached_data = data
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        length = len(data) if hasattr(data, "__len__") else 0
        return f"Data successfully stored in {CACHE_FILE} with {length} records."
    except Exception as exc:  # pragma: no cover - avoid failing on IO errors
        return f"Failed to store data in {CACHE_FILE}: {exc}"


def get_cached_data():
    """Load the cached dataset from disk if needed and return it."""
    global cached_data
    if cached_data is None and os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as fh:
            cached_data = json.load(fh)
    return cached_data


def head_cached_data(n: int = 10):
    """Return the first ``n`` rows from the cached dataset along with a message."""
    data = get_cached_data()
    if data is None:
        return {"message": "No cached data available.", "data": None}
    import pandas as pd

    df = pd.DataFrame(data)
    subset = df.head(n).to_dict(orient="list")
    return {
        "message": f"Returned the first {n} rows of cached data.",
        "data": subset,
    }


__all__ = [
    "store_cached_data",
    "get_cached_data",
    "head_cached_data",
    "cached_data",
    "CACHE_FILE",
]
