cached_data = None


def store_cached_data(data):
    """Store data in the global cache and return a status message."""
    global cached_data
    cached_data = data
    length = len(data) if hasattr(data, "__len__") else 0
    return {"status": "stored", "records": length}


def get_cached_data():
    """Return the cached dataset."""
    return cached_data


def head_cached_data(n: int = 10):
    """Return the first ``n`` rows from the cached dataset."""
    if cached_data is None:
        return None
    import pandas as pd

    df = pd.DataFrame(cached_data)
    return df.head(n).to_dict(orient="list")


__all__ = ["store_cached_data", "get_cached_data", "head_cached_data", "cached_data"]
