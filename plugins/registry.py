from __future__ import annotations

from typing import Dict, List, Optional

from plugins.base import Plugin
from storage.repository import Repository
from plugins.validation import validate_input, validate_output
from utils.errors import PluginNotFoundError


class PluginRegistry:
    def __init__(self, repository: Repository) -> None:
        self._plugins: Dict[str, Plugin] = {}
        self._repository = repository

    def register(self, plugin: Plugin, capabilities: Optional[List[str]] = None) -> None:
        existing = self._plugins.get(plugin.name)
        if existing is not None and existing.version != plugin.version:
            raise ValueError(f"Plugin conflict for {plugin.name}")
        self._plugins[plugin.name] = plugin
        self._repository.register_plugin(plugin.name, plugin.version, plugin.description)
        if capabilities:
            self._repository.register_plugin_capabilities(plugin.name, capabilities)

    def get(self, name: str) -> Plugin:
        plugin = self._plugins.get(name)
        if plugin is None:
            raise PluginNotFoundError(f"Plugin {name} not registered")
        return plugin

    def list_plugins(self) -> List[dict]:
        return self._repository.list_plugins()

    def get_details(self, name: str) -> dict:
        plugin = self.get(name)
        capabilities = self._repository.list_plugin_capabilities(name)
        return {
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "capabilities": capabilities,
        }

    async def run(self, name: str, payload: dict) -> dict:
        plugin = self.get(name)
        validated = validate_input(plugin, payload)
        result = await plugin.run(validated)
        return validate_output(plugin, result)
