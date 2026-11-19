# Local MCP Server

`mcp_local` provides a framework-neutral MCP server for inspecting benchmark
data. It runs one selected data adapter and exposes a common set of MCP tools
for that adapter.

An MCP client or agent framework connects to the server, discovers those tools,
and calls them over Streamable HTTP. The MCP server translates each request into
the selected adapter's implementation.

## Purpose

The container separates framework code from data-source code:

```text
Framework agent
  -> MCP client / adapter
  -> MCP server
  -> selected data adapter
  -> local CSV file or other data source
```

This allows the framework to use the same MCP tool names while the MCP adapter
handles format-specific details. For example, `preview_object` can read CSV
rows in Python, while a future SQLite adapter can execute `SELECT` statements.

## Current layout

```text
mcp_local/
├── README.md
├── Dockerfile
├── requirements.txt
├── decider.py
├── base_mcp_tools.py
├── adapters/
│   ├── __init__.py
│   └── csv_tools.py
└── adapter_env/
    ├── csv.env
    └── sqlite.env
```

The folder has no separate server entrypoint module anymore. The Dockerfile
starts `decider.py`, which both selects the adapter and starts FastMCP.

## Files

### `decider.py`

`decider.py` is the MCP container entrypoint.

It:

1. Reads `DATABASE`, defaulting to `CSV`.
2. Looks up the adapter in `BACKEND_MODULES`.
3. Imports the adapter module with `importlib`.
4. Retrieves the adapter class with `getattr`.
5. Instantiates the adapter.
6. Verifies that it inherits from `MCPTools`.
7. Registers the common tool names in `TOOL_NAMES`.
8. Starts the FastMCP Streamable HTTP server.

The current registry contains:

```python
"CSV": {
    "module": "adapters.csv_tools",
    "class": "CSVTools",
    "is_local": True,
}
```

It also contains a SQLite registry entry, but no
`adapters/sqlite_tools.py` implementation currently exists. Selecting
`DATABASE=SQLITE` therefore raises a module-not-found or missing-class error.

The server is created with `MCP_HOST` and `MCP_PORT`, defaulting to
`0.0.0.0:8000`.

### `base_mcp_tools.py`

`base_mcp_tools.py` defines the abstract `MCPTools` interface.

Every concrete adapter should implement these shared tools:

| Tool | Parameters | Return |
|---|---|---|
| `check_is_local` | none | `bool` |
| `list_data_sources` | none | `list[str]` |
| `get_source_metadata` | `source: str` | `dict[str, Any]` |
| `list_objects` | `source: str \| None = None` | `list[str]` |
| `describe_object` | `source: str` | `dict[str, Any]` |
| `preview_object` | `source: str`, `limit: int = 20` | `list[dict[str, Any]]` |
| `count_records` | `source: str` | `int` |
| `search_records` | `source: str`, `column: str`, `value: str`, `limit: int = 20` | `list[dict[str, Any]]` |
| `summarize_objects` | `source: str` | `dict[str, Any]` |
| `validate_sources` | none | `dict[str, Any]` |
| `check_source_status` | none | `dict[str, Any]` |

The abstract base class requires implementations to exist but does not fully
enforce parameter compatibility at runtime. Concrete methods should therefore
match these signatures exactly.

`dict[str, Any]` allows format-specific metadata fields. `list[dict[str, Any]]`
standardizes record previews and search results across formats.

### `adapters/`

The `adapters` package contains format-specific implementations of
`MCPTools`.

#### `adapters/__init__.py`

Marks `adapters` as an explicit Python package.

#### `adapters/csv_tools.py`

`CSVTools` implements the shared interface for local CSV files.

It reads these environment values:

```dotenv
CSV_DATA_DIR=/app/data/csv
CSV_ENCODING=utf-8
CSV_DELIMITER=,
CSV_PREVIEW_LIMIT=20
CSV_MAX_RESULTS=100
```

It provides:

- CSV discovery beneath `CSV_DATA_DIR`
- Source metadata
- Object/list operations
- Column and row-count descriptions
- Bounded previews
- Record counts
- Exact column/value searching
- Basic column summaries
- Source validation
- Source availability status

The `_resolve_source` method prevents a requested source from escaping
`CSV_DATA_DIR`. It rejects absolute or parent-directory paths and requires a
`.csv` file.

The private helper methods are not MCP tools:

- `_read_limit`
- `_resolve_source`
- `_source_name`
- `_read_rows`

`__init__` is the class constructor. It runs once when `CSVTools()` is
instantiated. It reads and validates configuration and stores it on the backend
instance.

CSV read operations require no MCP-specific package other than the MCP server
itself; CSV parsing uses Python's standard `csv` module.

### `adapter_env/csv.env`

Contains CSV-specific environment values loaded with Docker Compose's
`env_file`.

The file does not create a database or copy data. It configures the existing
CSV adapter.

`CSV_PREVIEW_LIMIT` is read by `CSVTools.__init__`, but the current
`preview_object(source, limit=20)` implementation uses its method argument and
caps it through `CSV_MAX_RESULTS`. Until `preview_object` is changed to use
`CSV_PREVIEW_LIMIT` as its default, this setting does not currently control the
default preview call.

### `adapter_env/sqlite.env`

Reserved for SQLite-specific environment values. It is currently empty.

No SQLite implementation exists, so this file should not be loaded until
`adapters/sqlite_tools.py` and `SQLiteTools` have been implemented.

### `Dockerfile`

The Dockerfile builds the MCP application image:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY base_mcp_tools.py decider.py ./
COPY adapters ./adapters
```

It copies executable application code, the base interface, and adapter modules
into the image.

It does not copy fixture data. Local dataset files should be mounted at runtime.

The container's default command is:

```dockerfile
CMD ["python", "-u", "decider.py"]
```

It declares port `8000` for documentation:

```dockerfile
EXPOSE 8000
```

`EXPOSE` does not publish or expose the port outside Docker. Docker Compose
controls that through `expose` or `ports`.

### `requirements.txt`

The container installs:

```text
mcp>=1.9,<2
```

This supplies the FastMCP server and MCP protocol implementation.

Adapter dependencies should be added separately if/when adapters need them.
For example, SQLite normally needs no third-party package, while MongoDB would
need an official MongoDB driver.

## Docker Compose integration

The current Compose service starts `mcp_local` as an internal service:

```yaml
mcp_local:
  build: ./mcp_local
  container_name: mcp_local
  environment:
    PYTHONDONTWRITEBYTECODE: "1"
    DATABASE: CSV
    MCP_HOST: 0.0.0.0
    MCP_PORT: "8000"
  env_file:
    - ./mcp_local/adapter_env/csv.env
  expose:
    - "8000"
  volumes:
    - ./data:/app/data:ro
```

### Mount and environment relationship

The mount:

```yaml
- ./data:/app/data:ro
```

maps the host repository's `./data` directory to `/app/data` inside the
container.

`CSV_DATA_DIR` says which mounted subdirectory the CSV adapter should search:

```dotenv
CSV_DATA_DIR=/app/data/csv
```

Therefore, this host layout:

```text
data/
└── csv/
    └── customers.csv
```

appears inside the container as:

```text
/app/data/csv/customers.csv
```

The mount is currently broader than `CSV_DATA_DIR`: it exposes `/app/data`,
including any other data under `./data`. Adapter code then restricts CSV
operations to `/app/data/csv`. A stronger mount boundary is:

```yaml
- ./data/csv:/app/data/csv:ro
```

This exposes only CSV fixture files to the MCP container.

The MCP endpoint is available to containers on the same Compose network at:

```text
http://mcp_local:8000/mcp
```

It is not published to the host because `expose` is used instead of `ports`.

## Startup flow

```text
Docker starts python decider.py
        |
        v
Read DATABASE
        |
        v
Load BACKEND_MODULES entry
        |
        v
Import adapters/csv_tools.py
        |
        v
Instantiate CSVTools
        |
        v
CSVTools reads CSV_* environment values
        |
        v
Register shared MCP tool methods
        |
        v
Start FastMCP on 0.0.0.0:8000
        |
        v
Accept initialize, tools/list, and tools/call requests
```

Tool discovery does not execute the tools. Discovery returns names,
descriptions, and JSON input/output schemas. A tool executes only after an MCP
client sends `tools/call`.

## MCP tool flow

```text
Framework MCP client
  -> tools/list
  -> sees CSVTools methods
  -> model chooses a tool
  -> tools/call
  -> FastMCP finds registered bound method
  -> CSVTools implementation runs
  -> result is serialized by FastMCP
  -> framework receives the result
```

FastMCP receives bound methods such as:

```python
backend.preview_object
```

The bound method remains attached to the `CSVTools` instance, including its
data directory and result limits.

Private Python helpers such as `_resolve_source` are not MCP tools. They are
called internally by public tool implementations.

## Running locally

Create the CSV fixture directory and at least one test file:

```bash
mkdir -p data/csv
```

Example CSV:

```text
data/csv/customers.csv
```

```csv
id,status,total
1,active,10
2,inactive,20
```

Build and start:

```bash
docker compose build mcp_local
docker compose up mcp_local
```

The MCP service endpoint is on the Compose network:

```text
http://mcp_local:8000/mcp
```

Host applications do not need access unless a host-published port is explicitly
configured.

Docker remains necessary for the host-to-container bind mount. `decider.py`
cannot create that mount after the container process starts.

## Adding another adapter

An adapter is a Python class that implements `MCPTools`.

1. Add a module below `adapters/`, for example
   `adapters/sqlite_tools.py`.
2. Add a class that inherits from `MCPTools`.
3. Implement the shared abstract methods.
4. Add adapter-prefixed settings to
   `adapter_env/sqlite.env`.
5. Add the module and class to `BACKEND_MODULES` in `decider.py`.
6. Load the appropriate env file in Docker Compose.
7. Add required mount or network configuration to Docker Compose.
8. Set `DATABASE=SQLITE`.

Example registry entry:

```python
"SQLITE": {
    "module": "adapters.sqlite_tools",
    "class": "SQLiteTools",
    "is_local": True,
}
```

The adapter should not start another FastMCP server. `decider.py` creates the
server and registers the adapter's bound methods.

## Current limitations

- No `adapters/sqlite_tools.py` or `SQLiteTools` exists.
- The SQLite env file is empty.
- No CSV fixture directory or files currently exist in the workspace.
- Compose loads both CSV and SQLite env files, although only CSV is selected.
- The data mount is broader than `/app/data/csv`; code currently enforces the
  narrower CSV source boundary.
- `CSV_PREVIEW_LIMIT` is stored but is not currently the default used by
  `preview_object`.
- No Docker health check exists for MCP startup/readiness.
- Framework workers do not currently receive `MCP_URL`.
- LangChain is not yet an MCP client in `langchain_logic.py`.
- Redis data bookkeeping is incomplete and separate from MCP tool behavior.
- Framework tool adapters are not yet implemented.

## Security and deployment notes

- Mount fixed CSV fixtures read-only.
- Validate every source before opening it.
- Reject absolute paths and parent-directory traversal.
- Keep result limits enabled.
- Do not expose arbitrary file-reading or shell-execution tools.
- Do not put database credentials or API keys in committed env files.
- Use Docker secrets or a secret manager for credentials.
- Bind network publishing only if host access is intentional.
- For local-only benchmark access, keep `expose: ["8000"]`.
- Prefer separate containers or services for strong backend isolation.
