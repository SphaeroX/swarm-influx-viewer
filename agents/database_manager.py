import os
import re
import influxdb_client
from swarm import Agent
from .common import MODEL_NAME

try:
    from config import (
        INFLUX_URL,
        INFLUX_TOKEN,
        INFLUX_ORG,
        INFLUX_BUCKET,
        MEASUREMENT,
    )
except ImportError:  # pragma: no cover - fallback for runtime usage
    INFLUX_URL = os.getenv("INFLUX_URL")
    INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
    INFLUX_ORG = os.getenv("INFLUX_ORG")
    INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")
    MEASUREMENT = os.getenv("MEASUREMENT")


def influx_list_buckets():
    """List all buckets in the InfluxDB instance."""
    client = influxdb_client.InfluxDBClient(
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
    client = influxdb_client.InfluxDBClient(
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
    client = influxdb_client.InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG
    )
    query_api = client.query_api()
    result = query_api.query(org=INFLUX_ORG, query=query)
    return [record.get_value() for table in result for record in table.records]


def influx_query_last_hour(field: str, measurement: str | None = None):
    """Query the specified field from the last hour."""
    measurement = measurement or MEASUREMENT
    query = f"""
from(bucket: \"{INFLUX_BUCKET}\")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == \"{measurement}\" and r._field == \"{field}\")
"""
    client = influxdb_client.InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG
    )
    query_api = client.query_api()
    result = query_api.query(org=INFLUX_ORG, query=query)
    return [
        {"time": record.get_time(), "value": record.get_value()}
        for table in result for record in table.records
    ]


def influx_query(flux_query: str):
    """Execute an arbitrary Flux query against the bucket."""
    if "from(bucket:" not in flux_query:
        flux_query = f'from(bucket: \"{INFLUX_BUCKET}\")\n  |> ' + flux_query.lstrip()
    else:
        flux_query = re.sub(
            r'from\(bucket:\s*(""|None|"?INFLUX_BUCKET"?)\)',
            f'from(bucket: \"{INFLUX_BUCKET}\")',
            flux_query,
            count=1,
        )

    client = influxdb_client.InfluxDBClient(
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
    client = influxdb_client.InfluxDBClient(
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
    client = influxdb_client.InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG
    )
    delete_api = client.delete_api()
    delete_api.delete(start, stop, predicate, bucket=INFLUX_BUCKET, org=INFLUX_ORG)
    return {"status": "deleted", "start": start, "stop": stop, "predicate": predicate}


influxDB_agent = Agent(
    name="InfluxDB Management Agent",
    instructions=(
        "You are an IT specialist agent capable of managing and querying an InfluxDB database. "
        "You can list buckets, measurements, fields, query the last hour of data, execute arbitrary Flux queries, "
        "write points, and delete data."
    ),
    functions=[
        influx_list_buckets,
        influx_list_measurements,
        influx_list_fields,
        influx_query_last_hour,
        influx_query,
        influx_write_point,
        influx_delete_data,
    ],
    model=MODEL_NAME,
)
