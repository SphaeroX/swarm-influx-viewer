### Install
1. ``pip install git+https://github.com/openai/swarm.git``
2. ``pip install Swarm``
3. ``pip install playwright swarm openai beautifulsoup4``
4. ``playwright install``

### Configuration
Copy `config.example.py` to `config.py` and fill in your InfluxDB details. If no
`config.py` is present, the application falls back to the environment variables
`INFLUX_URL`, `INFLUX_TOKEN`, `INFLUX_ORG` and `INFLUX_BUCKET`.

### Notes
The `influx_query` function now automatically injects the configured bucket if the Flux query does not specify one or if the placeholder `INFLUX_BUCKET` is used.
