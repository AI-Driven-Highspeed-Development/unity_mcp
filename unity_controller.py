"""
Unity MCP Controller - Business logic for Unity module registry operations.

Provides operations for querying and managing the Unity module registry.
All MCP tool implementations delegate to this controller.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from utils.logger_util import Logger

from managers.unity_module_registry_manager import (
    UnityModule,
    UnityModuleRegistryError,
    UnityModuleRegistryManager,
)

log = Logger(name="UnityController", verbose=False)


class UnityController:
    """
    Controller for Unity module registry operations.
    
    Provides high-level operations for AI agents to query and manage
    the Unity module registry.
    """
    
    # Valid module types for filtering
    VALID_TYPES: set[str] = {"core", "manager", "shared", "feature", "level", "thirdparty", "extension"}
    
    def __init__(self, unity_project_path: str | Path | None = None):
        """Initialize controller with optional Unity project path override."""
        self._registry: UnityModuleRegistryManager | None = None
        self._unity_project_path = unity_project_path
    
    def _get_registry(self) -> UnityModuleRegistryManager:
        """Get or create the registry manager instance."""
        if self._registry is None:
            self._registry = UnityModuleRegistryManager(
                unity_project_path=self._unity_project_path,
                verbose=False
            )
        return self._registry
    
    def _module_to_dict(self, module: UnityModule) -> dict[str, Any]:
        """Convert UnityModule dataclass to dict for JSON serialization."""
        return {
            "name": module.name,
            "type": module.type,
            "path": module.path,
            "has_yaml": module.has_yaml,
            "version": module.version,
            "description": module.description,
            "dependencies": module.dependencies,
            "assembly": module.assembly,
        }
    
    # --- Query Operations ---
    
    def list_modules(self, types: list[str] | None = None) -> dict[str, Any]:
        """
        List Unity modules, optionally filtered by type.
        
        Args:
            types: Optional list of module types to filter by.
                   Valid types: core, manager, shared, feature, level, thirdparty, extension
        
        Returns:
            dict with success status and list of modules.
        """
        try:
            registry = self._get_registry()
            
            # Validate types if provided
            if types:
                invalid_types = set(types) - self.VALID_TYPES
                if invalid_types:
                    return {
                        "success": False,
                        "error": f"Invalid module types: {sorted(invalid_types)}. "
                                 f"Valid types: {sorted(self.VALID_TYPES)}"
                    }
            
            # Get modules (apply filter if types provided)
            if types:
                modules = []
                for t in types:
                    modules.extend(registry.get_modules(module_type=t))
            else:
                modules = registry.get_modules()
            
            return {
                "success": True,
                "count": len(modules),
                "modules": [self._module_to_dict(m) for m in modules],
            }
        except UnityModuleRegistryError as e:
            log.error(f"Registry error listing modules: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            log.error(f"Unexpected error listing modules: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}
    
    def get_module(self, name: str) -> dict[str, Any]:
        """
        Get details for a single module by name.
        
        Args:
            name: Module name to look up.
        
        Returns:
            dict with success status and module details.
        """
        try:
            registry = self._get_registry()
            module = registry.get_module(name)
            
            if module is None:
                return {
                    "success": False,
                    "error": f"Module '{name}' not found in registry."
                }
            
            return {
                "success": True,
                "module": self._module_to_dict(module),
            }
        except UnityModuleRegistryError as e:
            log.error(f"Registry error getting module '{name}': {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            log.error(f"Unexpected error getting module '{name}': {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}
    
    def get_module_dependencies(self, name: str) -> dict[str, Any]:
        """
        Get dependencies for a module.
        
        Args:
            name: Module name to get dependencies for.
        
        Returns:
            dict with success status and list of dependency paths.
        """
        try:
            registry = self._get_registry()
            module = registry.get_module(name)
            
            if module is None:
                return {
                    "success": False,
                    "error": f"Module '{name}' not found in registry."
                }
            
            dependencies = registry.get_module_dependencies(name)
            
            return {
                "success": True,
                "module": name,
                "dependencies": dependencies,
                "count": len(dependencies),
            }
        except UnityModuleRegistryError as e:
            log.error(f"Registry error getting dependencies for '{name}': {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            log.error(f"Unexpected error getting dependencies for '{name}': {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}
    
    def find_dependents(self, name: str) -> dict[str, Any]:
        """
        Find modules that depend on a given module.
        
        Args:
            name: Module name or path to search for in dependencies.
        
        Returns:
            dict with success status and list of dependent modules.
        """
        try:
            registry = self._get_registry()
            dependents = registry.find_dependents(name)
            
            return {
                "success": True,
                "module": name,
                "dependents": [self._module_to_dict(m) for m in dependents],
                "count": len(dependents),
            }
        except UnityModuleRegistryError as e:
            log.error(f"Registry error finding dependents for '{name}': {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            log.error(f"Unexpected error finding dependents for '{name}': {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}
    
    # --- Registry Management Operations ---
    
    def refresh_registry(self) -> dict[str, Any]:
        """
        Rescan the Unity project and update the registry.
        
        Returns:
            dict with success status and scan summary (added/removed/unchanged counts).
        """
        try:
            registry = self._get_registry()
            
            # Get old module names for comparison
            old_module_names = {m.name for m in registry.modules}
            
            # Perform scan
            new_modules = registry.scan_modules()
            new_module_names = {m.name for m in new_modules}
            
            # Calculate diff
            added = new_module_names - old_module_names
            removed = old_module_names - new_module_names
            unchanged = old_module_names & new_module_names
            
            # Save updated registry
            registry.save_registry()
            
            log.info(f"Registry refreshed: {len(added)} added, {len(removed)} removed, {len(unchanged)} unchanged")
            
            return {
                "success": True,
                "summary": {
                    "added": len(added),
                    "removed": len(removed),
                    "unchanged": len(unchanged),
                    "total": len(new_modules),
                },
                "added_modules": sorted(added),
                "removed_modules": sorted(removed),
                "last_scan": registry.last_scan.isoformat() if registry.last_scan else None,
            }
        except UnityModuleRegistryError as e:
            log.error(f"Registry error during refresh: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            log.error(f"Unexpected error during refresh: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}
    
    def get_registry_status(self) -> dict[str, Any]:
        """
        Get registry metadata and statistics.
        
        Returns:
            dict with success status and registry summary.
        """
        try:
            registry = self._get_registry()
            summary = registry.get_scan_summary()
            
            return {
                "success": True,
                **summary,
            }
        except UnityModuleRegistryError as e:
            log.error(f"Registry error getting status: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            log.error(f"Unexpected error getting status: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}


# --- Module-level singleton ---

_controller_instance: UnityController | None = None


def get_unity_controller(unity_project_path: str | Path | None = None) -> UnityController:
    """Get or create the UnityController singleton instance."""
    global _controller_instance
    if _controller_instance is None or unity_project_path is not None:
        _controller_instance = UnityController(unity_project_path)
    return _controller_instance
