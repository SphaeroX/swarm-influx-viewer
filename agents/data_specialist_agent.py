import os
import pandas as pd
import matplotlib.pyplot as plt
from swarm import Agent
from .common import MODEL_NAME_1
from .data_store import head_cached_data, CACHE_FILE


def list_data_fields(data: dict) -> dict:
    """List all available fields in the provided dataset with a message."""
    df = pd.DataFrame(data)
    fields = list(df.columns)
    return {"message": f"Found {len(fields)} fields.", "fields": fields}


def filter_data(data: dict, filters: dict) -> dict:
    """Filter the dataset based on provided criteria and describe the result."""
    df = pd.DataFrame(data)
    for field, condition in filters.items():
        df = df.query(condition)
    result = df.to_dict(orient="list")
    return {
        "message": f"Filtered data with {len(filters)} conditions resulting in {len(df)} rows.",
        "data": result,
    }


def visualize_data(data: dict, plot_type: str | None = None, filename: str | None = None) -> dict:
    """Generate a plot from the data, save it, and return a summary message."""
    df = pd.DataFrame(data)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if not plot_type:
        if len(numeric_cols) >= 2:
            plot_type = "scatter"
        elif numeric_cols:
            plot_type = "hist"
        else:
            plot_type = "bar"

    if not filename:
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"plot_{plot_type}_{timestamp}.png"

    plt.figure()
    if plot_type == "scatter":
        x, y = numeric_cols[:2]
        plt.scatter(df[x], df[y])
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(f"Scatter plot of {y} vs {x}")
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
    elif plot_type == "hist":
        col = numeric_cols[0]
        plt.hist(df[col], bins=10)
        plt.xlabel(col)
        plt.title(f"Histogram of {col}")
    elif plot_type == "pie":
        if categorical_cols and numeric_cols:
            labels = df[categorical_cols[0]]
            sizes = df[numeric_cols[0]]
            plt.pie(sizes, labels=labels, autopct="%1.1f%%")
            plt.title(f"Pie chart of {numeric_cols[0]} by {categorical_cols[0]}")
        else:
            raise ValueError(
                "Pie chart requires at least one categorical and one numeric column."
            )
    else:
        df.plot()
        plt.title("Default plot of dataset")

    plt.tight_layout()
    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath)
    plt.close()
    return {"message": f"Plot saved to {filepath}", "file": filepath}


data_specialist_agent = Agent(
    name="Data Specialist Agent",
    instructions=(
        "You are a data specialist agent. You can list data fields, filter datasets based on criteria, "
        "and autonomously decide which data to visualize. You generate plot files when requested, "
        "supporting scatter, line, bar, histogram and pie charts. "
        "Retrieved data is cached in the file "
        f"{CACHE_FILE}. Use head_cached_data to inspect the first rows. "
        "Start your analysis only when an actual dataset is provided. If no data is available, "
        "ask that it be retrieved via the database manager first."
    ),
    functions=[
        list_data_fields,
        filter_data,
        visualize_data,
        head_cached_data,
    ],
    model=MODEL_NAME_1,
)
