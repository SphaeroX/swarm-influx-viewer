import os
import re
from influxdb_client import InfluxDBClient
from datetime import datetime, timezone
from swarm import Agent
from .common import MODEL_NAME_1

try:
    from config import (
        INFLUX_URL,
        INFLUX_TOKEN,
        INFLUX_ORG,
        INFLUX_BUCKET,
        MEASUREMENT,
    )
except ImportError:  # pragma: no cover - fallback for runtime usage
    INFLUX_URL = os.getenv("INFLUX_URL", "")
    INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "")
    INFLUX_ORG = os.getenv("INFLUX_ORG", "")
    INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "")
    MEASUREMENT = os.getenv("MEASUREMENT", "")


def influx_list_buckets():
    """List all buckets in the InfluxDB instance."""
    client = InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG
    )
    buckets = client.buckets_api().find_buckets().buckets
    return [b.name for b in buckets]


def influx_list_measurements():
    """List all measurements in the predetermined bucket."""
    query = f"""
import \"influxdata/influxdb/schema\"
schema.measurements(bucket: \"{INFLUX_BUCKET}\")
"""
    client = InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG
    )
    query_api = client.query_api()
    result = query_api.query(org=INFLUX_ORG, query=query)
    return [record.get_value() for table in result for record in table.records]


def influx_list_fields(measurement: str | None = None):
    """List all field keys for a given measurement in the bucket."""
    measurement = measurement or MEASUREMENT
    query = f"""
import \"influxdata/influxdb/schema\"
schema.fieldKeys(
  bucket: \"{INFLUX_BUCKET}\",
  predicate: (r) => r._measurement == \"{measurement}\"
)
"""
    client = InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG
    )
    query_api = client.query_api()
    result = query_api.query(org=INFLUX_ORG, query=query)
    return [record.get_value() for table in result for record in table.records]





def influx_query(flux_query: str, measurement: str | None = None):
    """Execute an arbitrary Flux query against the bucket and measurement."""
    measurement = measurement or MEASUREMENT
    if "from(bucket:" not in flux_query:
        cleaned = flux_query.lstrip()
        if cleaned.startswith("|>"):
            cleaned = cleaned[len("|>"):].lstrip()
        flux_query = f'from(bucket: "{INFLUX_BUCKET}")\n  |> ' + cleaned
    else:
        flux_query = re.sub(
            r'from\(bucket:\s*(""|None|"?INFLUX_BUCKET"?)\)',
            f'from(bucket: "{INFLUX_BUCKET}")',
            flux_query,
            count=1,
        )

    measurement_placeholder = r'r\._measurement\s*==\s*(""|None|"?MEASUREMENT"?)'
    if re.search(measurement_placeholder, flux_query):
        flux_query = re.sub(
            measurement_placeholder,
            f'r._measurement == "{measurement}"',
            flux_query,
            count=1,
        )
    elif "_measurement" not in flux_query:
        flux_query = re.sub(
            r'(from\(bucket:[^\n]+\))',
            r'\1\n  |> filter(fn: (r) => r._measurement == "%s")' % measurement,
            flux_query,
            count=1,
        )

    client = InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG
    )
    query_api = client.query_api()
    result = query_api.query(org=INFLUX_ORG, query=flux_query)
    return [
        {**record.values, "value": record.get_value(), "time": record.get_time()}
        for table in result for record in table.records
    ]

def influx_write_point(fields: dict, measurement: str | None = None, tags: dict | None = None, time=None):
    """Write a single point to the bucket."""
    measurement = measurement or MEASUREMENT
    client = InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG
    )
    write_api = client.write_api()
    point = {
        "measurement": measurement,
        "tags": tags or {},
        "fields": fields,
        "time": time,
    }
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    return {"status": "success", "point": point}


def influx_delete_data(start: str, stop: str, predicate: str = ""):
    """Delete data in a time range with optional predicate."""
    client = InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG
    )
    delete_api = client.delete_api()
    delete_api.delete(start, stop, predicate, bucket=INFLUX_BUCKET, org=INFLUX_ORG)
    return {"status": "deleted", "start": start, "stop": stop, "predicate": predicate}


def get_current_time() -> str:
    """Return the current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


influxDB_agent = Agent(
    name="InfluxDB Management Agent",
    instructions=(
        "You are an IT specialist agent capable of managing and querying an InfluxDB database. "
        f"The server runs at {INFLUX_URL} with organisation {INFLUX_ORG}, bucket {INFLUX_BUCKET} "
        f"and default measurement {MEASUREMENT}. "
        "Authenticate using the token stored in the INFLUX_TOKEN environment variable. "
        "You can list buckets, measurements, fields, execute arbitrary Flux queries, write points, delete data, "
        "and provide the current UTC time."
    ),
    functions=[
        influx_list_buckets,
        influx_list_measurements,
        influx_list_fields,
        influx_query,
        influx_write_point,
        influx_delete_data,
        get_current_time,
    ],
    model=MODEL_NAME_1,
)
