import os

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    "local-tools",
    host=os.getenv("MCP_HOST", "0.0.0.0"), #0.0.0.0 means listen to all network interfaces like other containers on the network
    port=int(os.getenv("MCP_PORT", "8000")),
)


@mcp.tool()
def database_status() -> str:
    """Return the status of the local benchmark database."""
    return "ready"


@mcp.tool()
def echo(message: str) -> str:
    """Return a message unchanged for connectivity checks."""
    return message


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
