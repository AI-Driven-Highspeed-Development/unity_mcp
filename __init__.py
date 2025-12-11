"""
Unity MCP - Model Context Protocol server for Unity module registry queries.

Provides tools for AI agents to query and manage the Unity module registry,
which tracks modules in a Unity project (cores, managers, features, etc.).

Usage as MCP Server:
    python -m mcps.unity_mcp.unity_mcp

Refresh to register in .vscode/mcp.json:
    python adhd_framework.py refresh --module unity_mcp

Usage as Library:
    from mcps.unity_mcp import UnityController, get_unity_controller
    controller = get_unity_controller()
    result = controller.list_modules(types=["feature", "manager"])
"""

import os
import sys

# Add path handling to work from the new nested directory structure
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.getcwd()  # Use current working directory as project root
sys.path.insert(0, project_root)

from mcps.unity_mcp.unity_mcp import mcp
from mcps.unity_mcp.unity_controller import UnityController, get_unity_controller
from mcps.unity_mcp.refresh import main as mcp_refresh_main

mcp_refresh_main()

__all__ = [
    "mcp",
    "UnityController",
    "get_unity_controller",
]