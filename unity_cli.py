"""CLI commands and registration for unity_adhd_mcp.

Exposes Unity ADHD MCP tools as CLI commands for command-line usage.
"""

from __future__ import annotations

import argparse
import json

from mcps.unity_adhd_mcp.unity_controller import UnityController
from managers.cli_manager import CLIManager, ModuleRegistration, Command, CommandArg


# ─────────────────────────────────────────────────────────────────────────────
# Controller Access
# ─────────────────────────────────────────────────────────────────────────────

_controller: UnityController | None = None


def _get_controller() -> UnityController:
    """Get or create the controller instance."""
    global _controller
    if _controller is None:
        _controller = UnityController()
    return _controller


def _print_result(result: dict) -> int:
    """Print result as JSON and return exit code."""
    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("success", True) else 1


# ─────────────────────────────────────────────────────────────────────────────
# Handler Functions
# ─────────────────────────────────────────────────────────────────────────────

def list_modules_cmd(args: argparse.Namespace) -> int:
    """List Unity modules."""
    types = args.types.split(",") if args.types else None
    result = _get_controller().list_modules(types=types)
    return _print_result(result)


def get_module_cmd(args: argparse.Namespace) -> int:
    """Get details for a single Unity module."""
    result = _get_controller().get_module(name=args.name)
    return _print_result(result)


def get_deps_cmd(args: argparse.Namespace) -> int:
    """Get dependencies for a Unity module."""
    result = _get_controller().get_module_dependencies(name=args.name)
    return _print_result(result)


def find_dependents_cmd(args: argparse.Namespace) -> int:
    """Find modules that depend on a given module."""
    result = _get_controller().find_dependents(name=args.name)
    return _print_result(result)


def refresh_registry_cmd(args: argparse.Namespace) -> int:
    """Rescan Unity project and update registry."""
    result = _get_controller().refresh_registry()
    return _print_result(result)


def get_status_cmd(args: argparse.Namespace) -> int:
    """Get registry status and statistics."""
    result = _get_controller().get_registry_status()
    return _print_result(result)


def generate_report_cmd(args: argparse.Namespace) -> int:
    """Generate markdown registry report."""
    result = _get_controller().generate_report()
    return _print_result(result)


# ─────────────────────────────────────────────────────────────────────────────
# CLI Registration
# ─────────────────────────────────────────────────────────────────────────────

def register_cli() -> None:
    """Register unity_adhd_mcp commands with CLIManager."""
    cli = CLIManager()
    cli.register_module(ModuleRegistration(
        module_name="unity_adhd_mcp",
        short_name="um",
        description="Unity module registry CLI",
        commands=[
            Command(
                name="list",
                help="List Unity modules",
                handler="mcps.unity_adhd_mcp.unity_cli:list_modules_cmd",
                args=[
                    CommandArg(
                        name="--types",
                        short="-t",
                        help="Comma-separated types: core,manager,shared,feature,level,thirdparty,extension",
                    ),
                ],
            ),
            Command(
                name="get",
                help="Get details for a Unity module",
                handler="mcps.unity_adhd_mcp.unity_cli:get_module_cmd",
                args=[
                    CommandArg(name="name", help="Module name"),
                ],
            ),
            Command(
                name="deps",
                help="Get dependencies for a Unity module",
                handler="mcps.unity_adhd_mcp.unity_cli:get_deps_cmd",
                args=[
                    CommandArg(name="name", help="Module name"),
                ],
            ),
            Command(
                name="dependents",
                help="Find modules that depend on a given module",
                handler="mcps.unity_adhd_mcp.unity_cli:find_dependents_cmd",
                args=[
                    CommandArg(name="name", help="Module name or path"),
                ],
            ),
            Command(
                name="refresh",
                help="Rescan Unity project and update registry",
                handler="mcps.unity_adhd_mcp.unity_cli:refresh_registry_cmd",
            ),
            Command(
                name="status",
                help="Get registry status and statistics",
                handler="mcps.unity_adhd_mcp.unity_cli:get_status_cmd",
            ),
            Command(
                name="report",
                help="Generate markdown registry report",
                handler="mcps.unity_adhd_mcp.unity_cli:generate_report_cmd",
            ),
        ],
    ))
