# Project Overview

This repository provides a set of LLM-driven agents for interacting with an InfluxDB instance and analysing time series data. The implementation uses the `swarm` library and defines several agents under the `agents` package:

- `database_manager.py` – functions to list buckets, measurements and fields, run custom Flux queries, write data and delete data. Wrapped as the `influxDB_agent`.
- `data_specialist_agent.py` – utilities to inspect, filter and plot data with pandas and matplotlib. Exposed as `data_specialist_agent`.
- `clarifying_agent.py` – simple helper to ask the user for additional details.
- `triage_agent.py` – initial contact agent that decides which specialist should handle the request.

The entry point `main.py` shows how to run the triage agent with Swarm. Configuration values for the InfluxDB connection are provided in `config.example.py`; a user can copy this to `config.py` or set environment variables instead.

Tests live in the `tests` directory and focus on verifying the database helper functions. Dependencies are listed in `requirements.txt`.

Use this file as a quick reference for the repository structure when extending or modifying the agents.

# SWARM Framework Usage

This project is built around the SWARM framework from OpenAI, which orchestrates multiple domain-specific agents to work together on a task. Each agent exposes a set of functions that can be chained by the framework to produce useful results.

When designing instructions for the agents, provide detailed context whenever possible. Examples include the current timestamp, relevant database connection details or other metadata required for the task. The large language model uses these details to craft accurate function calls and return valid results.

Supplying comprehensive instructions reduces ambiguity and improves the reliability of automated workflows driven by the SWARM framework.
