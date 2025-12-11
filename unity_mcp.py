"""
Unity MCP Server - FastMCP-based MCP server for Unity module registry queries.

This module provides the MCP server entry point using the FastMCP pattern.
Run with: python -m mcps.unity_mcp.unity_mcp
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcps.unity_mcp.unity_controller import UnityController

# Create MCP server instance
mcp = FastMCP(
    name="unity_mcp",
    instructions=(
        "Unity module registry MCP server. "
        "Use these tools to query and manage the Unity module registry, "
        "which tracks modules in a Unity project (cores, managers, features, etc.)."
    ),
)

# Module-level controller instance
_controller: UnityController | None = None


def _get_controller() -> UnityController:
    """Get or create the UnityController instance."""
    global _controller
    if _controller is None:
        _controller = UnityController()
    return _controller


# --- Query Tools ---


@mcp.tool()
def list_unity_modules(types: list[str] | None = None) -> dict:
    """List Unity modules, optionally filtered by type.
    
    Args:
        types: Optional list of module types to filter by.
               Valid types: core, manager, shared, feature, level, thirdparty, extension
    
    Returns:
        dict with success status, count, and list of modules
    """
    return _get_controller().list_modules(types=types)


@mcp.tool()
def get_unity_module(name: str) -> dict:
    """Get details for a single Unity module by name.
    
    Args:
        name: Module name to look up (e.g., "GameManager", "PlayerFeature")
    
    Returns:
        dict with success status and module details including type, path, dependencies
    """
    return _get_controller().get_module(name=name)


@mcp.tool()
def get_module_dependencies(name: str) -> dict:
    """Get the dependency list for a Unity module.
    
    Args:
        name: Module name to get dependencies for
    
    Returns:
        dict with success status and list of dependency paths
    """
    return _get_controller().get_module_dependencies(name=name)


@mcp.tool()
def find_dependents(name: str) -> dict:
    """Find Unity modules that depend on a given module.
    
    Use this to understand the impact of changing a module.
    
    Args:
        name: Module name or path to search for in dependencies
    
    Returns:
        dict with success status and list of dependent modules
    """
    return _get_controller().find_dependents(name=name)


# --- Registry Management Tools ---


@mcp.tool()
def refresh_unity_registry() -> dict:
    """Rescan the Unity project and update the module registry.
    
    Scans the Unity project's Assets folder for modules in:
    - Assets/_Core/ (core modules)
    - Assets/_Managers/ (manager modules)
    - Assets/_Shared/ (shared utilities)
    - Assets/Features/ (feature modules)
    - Assets/Levels/ (level content)
    - Assets/ThirdParty/ (external packages)
    - Assets/_Extensions/ (extensions)
    
    Returns:
        dict with success status and summary (added/removed/unchanged counts)
    """
    return _get_controller().refresh_registry()


@mcp.tool()
def get_registry_status() -> dict:
    """Get Unity module registry metadata and statistics.
    
    Returns:
        dict with total modules, counts by type, last scan time, and project path
    """
    return _get_controller().get_registry_status()


# --- Entry Point ---


def main() -> None:
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
