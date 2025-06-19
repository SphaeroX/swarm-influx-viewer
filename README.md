### Install
1. ``pip install git+https://github.com/openai/swarm.git``
2. ``pip install Swarm``
3. ``pip install playwright swarm openai beautifulsoup4``
4. ``playwright install``

### Configuration
Copy `config.example.py` to `config.py` and adjust the values directly. The
sample file defines plain constants and does not read from environment
variables. If `config.py` is absent, the application falls back to the
environment variables `INFLUX_URL`, `INFLUX_TOKEN`, `INFLUX_ORG`, `INFLUX_BUCKET`
and `MEASUREMENT`. The `MEASUREMENT` setting controls which measurement is used
when none is explicitly provided in a query.

Set `LLM_PROVIDER` to `openai` or `ollama` to explicitly choose between the two.
When omitted, the agents default to OpenAI if `OPENAI_API_KEY` is provided and
fall back to the local Ollama server defined by `OLLAMA_BASE_URL`.

You can define up to three model names for each provider with
`OPENAI_MODEL_NAME_1` through `OPENAI_MODEL_NAME_3` and their Ollama
equivalents. All agents currently use `MODEL_NAME_1` from the selected
provider.

### Notes
The `influx_query` function now automatically injects the configured bucket if the Flux query does not specify one or if the placeholder `INFLUX_BUCKET` is used. It also applies the configured measurement when no `_measurement` filter is present or when `MEASUREMENT` is used as a placeholder.

Query results retrieved with `influx_query_store` are saved to `cached_data.json` by default. The data analyst can load this file directly for further processing.

### Agents
Each agent now resides in its own module under the `agents` package:
- `database_manager.py` for database management
- `get_current_time` helper returns the current UTC time in ISO format
- `data_specialist_agent.py` for data analysis and plotting
- `clarifying_agent.py` for gathering missing user details
- `triage_agent.py` that routes requests to the appropriate agent
