# Unity ADHD MCP

Model Context Protocol server for Unity module registry queries.

## Overview

Exposes tools for AI agents to query and manage the Unity module registry maintained by `unity_module_registry_manager`. This enables AI assistants to understand the structure of a Unity project and navigate its module dependencies.

## Available Tools

| Tool | Parameters | Description |
|:-----|:-----------|:------------|
| `list_unity_modules` | `types?: list[str]` | List all modules, optionally filtered by type |
| `get_unity_module` | `name: str` | Get details for a single module |
| `get_module_dependencies` | `name: str` | Get dependency list for a module |
| `find_dependents` | `name: str` | Find modules that depend on a given module |
| `refresh_unity_registry` | None | Rescan Unity project and update registry |
| `get_registry_status` | None | Get registry metadata (last_scan, counts) |

## Module Types

The following Unity module types are supported:

| Type | Folder | Purpose |
|:-----|:-------|:--------|
| `core` | `Assets/_Core/` | Framework infrastructure |
| `manager` | `Assets/_Managers/` | Stateful singletons |
| `shared` | `Assets/_Shared/` | Reusable utilities |
| `feature` | `Assets/Features/` | Gameplay systems |
| `level` | `Assets/Levels/` | Level content |
| `thirdparty` | `Assets/ThirdParty/` | External packages |
| `extension` | `Assets/_Extensions/` | Extensions |

## Usage

### As MCP Server

```bash
python -m mcps.unity_adhd_mcp.unity_adhd_mcp
```

### As Library

```python
from mcps.unity_adhd_mcp import UnityController, get_unity_controller

controller = get_unity_controller()

# List all feature modules
result = controller.list_modules(types=["feature"])

# Get a specific module
module = controller.get_module("GameManager")

# Refresh registry from Unity project
summary = controller.refresh_registry()
```

## Module Structure

```
mcps/unity_adhd_mcp/
├── __init__.py           # Exports, path setup, auto-refresh
├── init.yaml             # Module metadata (type: mcp)
├── README.md             # This file
├── unity_adhd_mcp.py     # FastMCP server with tool decorators
├── unity_controller.py   # Business logic implementation
└── refresh.py            # Register in .vscode/mcp.json
```

## Dependencies

- `unity_module_registry_manager` - Registry storage and scanning (local)
- `logger_util` - Logging to stderr (MCP-safe)