import os
import re

try:
    from config import (
        INFLUX_URL,
        INFLUX_TOKEN,
        INFLUX_ORG,
        INFLUX_BUCKET,
        MEASUREMENT,
    )
except ImportError:
    INFLUX_URL = os.getenv("INFLUX_URL")
    INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
    INFLUX_ORG = os.getenv("INFLUX_ORG")
    INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")
    MEASUREMENT = os.getenv("MEASUREMENT")

from swarm import Swarm, Agent
from openai import OpenAI
import influxdb_client
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Ollama / Swarm client ----------
ollama_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL_NAME = "qwen3:8b"
client = Swarm(ollama_client)


# ---------- InfluxDB agent ----------


def influx_list_buckets():
    """List all buckets in the InfluxDB instance."""
    client = influxdb_client.InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    buckets = client.buckets_api().find_buckets().buckets
    return [b.name for b in buckets]


def influx_list_measurements():
    """List all measurements in the predetermined bucket."""
    query = f'''
import "influxdata/influxdb/schema"
schema.measurements(bucket: "{INFLUX_BUCKET}")
'''
    client = influxdb_client.InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()
    result = query_api.query(org=INFLUX_ORG, query=query)
    return [record.get_value() for table in result for record in table.records]


def influx_list_fields(measurement: str = None):
    """List all field keys for a given measurement in the bucket."""
    measurement = measurement or MEASUREMENT
    query = f'''
import "influxdata/influxdb/schema"
schema.fieldKeys(
  bucket: "{INFLUX_BUCKET}",
  predicate: (r) => r._measurement == "{measurement}"
)
'''
    client = influxdb_client.InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()
    result = query_api.query(org=INFLUX_ORG, query=query)
    return [record.get_value() for table in result for record in table.records]


def influx_query_last_hour(field: str, measurement: str | None = None):
    """Query the specified field from the last hour."""
    measurement = measurement or MEASUREMENT
    query = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "{measurement}" and r._field == "{field}")
'''
    client = influxdb_client.InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()
    result = query_api.query(org=INFLUX_ORG, query=query)
    return [
        {"time": record.get_time(), "value": record.get_value()}
        for table in result for record in table.records
    ]


def influx_query(flux_query: str):
    """Execute an arbitrary Flux query against the bucket.

    If no bucket is specified in the given query, or an empty bucket is provided,
    the configured ``INFLUX_BUCKET`` will be inserted automatically. This helps
    avoid ``ApiException`` errors caused by missing bucket information.
    """
    if "from(bucket:" not in flux_query:
        flux_query = f'from(bucket: "{INFLUX_BUCKET}")\n  |> ' + flux_query.lstrip()
    else:
        flux_query = re.sub(
            r'from\(bucket:\s*(""|None|"?INFLUX_BUCKET"?)\)',
            f'from(bucket: "{INFLUX_BUCKET}")',
            flux_query,
            count=1,
        )

    client = influxdb_client.InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()
    result = query_api.query(org=INFLUX_ORG, query=flux_query)
    return [
        {**record.values, "value": record.get_value(), "time": record.get_time()}
        for table in result for record in table.records
    ]


def influx_write_point(fields: dict, measurement: str | None = None, tags: dict = None, time=None):
    """Write a single point to the bucket."""
    measurement = measurement or MEASUREMENT
    client = influxdb_client.InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api()
    point = {
        "measurement": measurement,
        "tags": tags or {},
        "fields": fields,
        "time": time
    }
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
    return {"status": "success", "point": point}


def influx_delete_data(start: str, stop: str, predicate: str = ""):
    """Delete data in a time range with optional predicate."""
    client = influxdb_client.InfluxDBClient(
        url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    delete_api = client.delete_api()
    delete_api.delete(start, stop, predicate,
                      bucket=INFLUX_BUCKET, org=INFLUX_ORG)
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


# ---------- Data Specialist agent ----------

def list_data_fields(data: dict) -> list:
    """List all available fields in the provided dataset."""
    df = pd.DataFrame(data)
    return list(df.columns)


def filter_data(data: dict, filters: dict) -> dict:
    """Filter the dataset based on provided criteria."""
    df = pd.DataFrame(data)
    for field, condition in filters.items():
        df = df.query(condition)
    return df.to_dict(orient="list")


def visualize_data(data: dict, plot_type: str = None, filename: str = None) -> str:
    """Generate a plot from the data and save it to a file.

    The agent decides plot type if not specified and chooses relevant fields.
    Supports scatter, line, bar, histogram, pie, and default plots.
    Returns the filepath of the saved plot.
    """
    df = pd.DataFrame(data)

    # Determine default plot type and columns if not provided
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(
        include=["object", "category"]).columns.tolist()

    if not plot_type:
        if len(numeric_cols) >= 2:
            plot_type = "scatter"
        elif numeric_cols:
            plot_type = "hist"
        else:
            plot_type = "bar"

    # Create filename if not provided
    if not filename:
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        filename = f"plot_{plot_type}_{timestamp}.png"

    plt.figure()
    # Scatter plot
    if plot_type == "scatter":
        x, y = numeric_cols[:2]
        plt.scatter(df[x], df[y])
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(f"Scatter plot of {y} vs {x}")

    # Line plot
    elif plot_type == "line":
        if len(numeric_cols) >= 2:
            x, y = numeric_cols[:2]
            plt.plot(df[x], df[y])
            plt.xlabel(x)
            plt.ylabel(y)
            plt.title(f"Line plot of {y} vs {x}")
        else:
            col = numeric_cols[0]
            plt.plot(df[col])
            plt.xlabel("index")
            plt.ylabel(col)
            plt.title(f"Line plot of {col}")

    # Bar chart
    elif plot_type == "bar":
        if categorical_cols and numeric_cols:
            x = categorical_cols[0]
            y = numeric_cols[0]
            plt.bar(df[x], df[y])
            plt.xlabel(x)
            plt.ylabel(y)
            plt.title(f"Bar chart of {y} by {x}")
        else:
            df.plot(kind="bar")
            plt.title("Bar chart of dataset")

    # Histogram
    elif plot_type == "hist":
        col = numeric_cols[0]
        plt.hist(df[col], bins=10)
        plt.xlabel(col)
        plt.title(f"Histogram of {col}")

    # Pie chart
    elif plot_type == "pie":
        if categorical_cols and numeric_cols:
            labels = df[categorical_cols[0]]
            sizes = df[numeric_cols[0]]
            plt.pie(sizes, labels=labels, autopct='%1.1f%%')
            plt.title(
                f"Pie chart of {numeric_cols[0]} by {categorical_cols[0]}")
        else:
            raise ValueError(
                "Pie chart requires at least one categorical and one numeric column.")

    # Default fallback
    else:
        df.plot()
        plt.title("Default plot of dataset")

    plt.tight_layout()
    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath)
    plt.close()
    return filepath


# Define the agent with its capabilities

data_specialist_agent = Agent(
    name="Data Specialist Agent",
    instructions=(
        "You are a data specialist agent. You can list data fields, filter datasets based on criteria, "
        "and autonomously decide which data to visualize. You generate plot files when requested, "
        "supporting scatter, line, bar, histogram and pie charts."
    ),
    functions=[
        list_data_fields,
        filter_data,
        visualize_data,
    ],
    model=MODEL_NAME,
)

# ---------- Triage agent ----------

triage_agent = Agent(
    name="Triage Agent",
    instructions="Determine which agent is best suited to handle the user's request, and transfer the conversation to that agent.",
    model=MODEL_NAME,
)


# ---------- Transfer functions ----------
def transfer_back_to_triage():
    """Call this function if a user is asking about a topic that is not handled by the current agent."""
    return triage_agent


def transfer_to_database_manager():
    """Transfer the conversation to the InfluxDB management agent."""
    return influxDB_agent


def transfer_to_data_specialist():
    """Transfer the conversation to the Data Specialist agent."""
    return data_specialist_agent


triage_agent.functions = [
    transfer_to_database_manager, transfer_to_data_specialist]
influxDB_agent.functions.append(transfer_back_to_triage)
influxDB_agent.functions.append(transfer_to_data_specialist)
data_specialist_agent.functions.append(transfer_back_to_triage)
