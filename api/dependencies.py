from __future__ import annotations

from typing import Optional

from cache.memory import InMemoryCache
from execution.engine import WorkflowEngine
from plugins.builtin import register_builtin_plugins
from plugins.pack import register_plugin_pack
from plugins.registry import PluginRegistry
from storage.db import init_db
from storage.repository import Repository

_repository: Optional[Repository] = None
_registry: Optional[PluginRegistry] = None
_cache: Optional[InMemoryCache] = None
_engine: Optional[WorkflowEngine] = None


def get_repository() -> Repository:
    global _repository
    if _repository is None:
        init_db()
        _repository = Repository()
    return _repository


def get_registry() -> PluginRegistry:
    global _registry
    if _registry is None:
        _registry = PluginRegistry(get_repository())
        register_builtin_plugins(_registry)
        register_plugin_pack(_registry)
    return _registry


def get_cache() -> InMemoryCache:
    global _cache
    if _cache is None:
        _cache = InMemoryCache()
    return _cache


def get_engine() -> WorkflowEngine:
    global _engine
    if _engine is None:
        _engine = WorkflowEngine(
            repository=get_repository(),
            registry=get_registry(),
            cache=get_cache(),
        )
    return _engine
