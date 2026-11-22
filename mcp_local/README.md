# MCP Local

`mcp_local` runs a local MCP server that exposes database data through a consistent set of tools. The shared interface covers source discovery, metadata, object inspection, previews, counts, searches, summaries, validation, and status checks.

## How it works

`decider.py` reads the `DATABASE` environment variable and loads the matching adapter:

- `CSV` uses `adapters/csv_tools.py` to read CSV files.
- `SQLite` is listed for future support; its adapter is not implemented yet.

The selected adapter implements `MCPTools` from `base_mcp_tools.py`. The server then registers the available tools and listens on the configured MCP host and port.

## Data and configuration

Place local CSV files under `data/csv/`. Adapter settings are in `adapter_env/csv.env`, while `adapter_env/sqlite.env` can hold SQLite settings.

The Docker container mounts data read-only and defaults to the CSV backend. To change backends, set `DATABASE` in Docker Compose to `CSV` or a future supported value.
