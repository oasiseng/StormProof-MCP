"""StormProof MCP server — NOAA hurricane weather verification for AI assistants.

Exposes address + date lookups for historical wind, gust, and storm surge data
via the Model Context Protocol. Backed by the public StormProof preview API
maintained by Enrique Lairet, PE at hurricaneinspections.com.
"""

__version__ = "0.1.0"

from .server import mcp

__all__ = ["mcp", "__version__"]
