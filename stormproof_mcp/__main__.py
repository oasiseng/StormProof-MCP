"""Entrypoint for `python -m stormproof_mcp` and the `stormproof-mcp` CLI."""

from .server import mcp


def main() -> None:
    """Run the StormProof MCP server over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
