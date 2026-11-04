import os
import importlib

from mcp.server.fastmcp import FastMCP
from base_mcp_tools import MCPTools


BACKEND_MODULES = {
    "CSV": ("csv_tools", "CSVTools"),
    "SQLITE": ("sqlite_tools", "SQLiteTools"),
}

TOOL_NAMES = (
    "check_is_local",
    "list_data_sources",
    "get_source_metadata",
    "list_objects",
    "describe_object",
    "preview_object",
    "count_records",
    "search_records",
    "summarize_objects",
    "validate_sources",
    "check_source_status",
)


def load_backend(database_name: str) -> MCPTools:
    """Load the configured database backend implementation."""
    backend_config = BACKEND_MODULES.get(database_name.upper())
    if backend_config is None:
        supported = ", ".join(sorted(BACKEND_MODULES))
        raise ValueError(
            f"Unsupported DATABASE={database_name!r}. "
            f"Supported values: {supported}"
        )

    module_name, class_name = backend_config
    backend_module = importlib.import_module(module_name)
    backend_class = getattr(backend_module, class_name, None)

    if backend_class is None:
        raise AttributeError(
            f"Module {module_name!r} does not define {class_name!r}"
        )

    backend = backend_class()
    if not isinstance(backend, MCPTools):
        raise TypeError(
            f"{module_name}.{class_name} must inherit from MCPTools"
        )

    return backend


def register_backend_tools(
    mcp: FastMCP,
    backend: MCPTools,
) -> None:
    """Register every interface method on the shared MCP server."""
    for tool_name in TOOL_NAMES:
        tool = getattr(backend, tool_name)
        if not callable(tool):
            raise TypeError(f"Backend tool {tool_name!r} is not callable")

        mcp.tool(name=tool_name)(tool)


def create_server() -> FastMCP:
    """Create and configure the MCP server for the selected backend."""
    database_name = os.getenv("DATABASE", "CSV").strip().upper()
    backend = load_backend(database_name)

    mcp = FastMCP(
        f"{database_name.lower()}-tools",
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", "8000")),
    )
    register_backend_tools(mcp, backend)
    return mcp


if __name__ == "__main__":
    create_server().run(transport="streamable-http")