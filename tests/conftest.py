import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.dependencies import get_cache, get_engine, get_registry, get_repository
from api.main import create_app
from cache.memory import InMemoryCache
from execution.engine import WorkflowEngine
from plugins.builtin import register_builtin_plugins
from plugins.extra_plugins import register_extra_plugins
from plugins.pack import register_plugin_pack
from plugins.registry import PluginRegistry
from storage.db import init_db
from storage.repository import Repository


@pytest.fixture()
def repository(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(force=True, database_url=f"sqlite:///{db_path}")
    return Repository()


@pytest.fixture()
def registry(repository):
    registry = PluginRegistry(repository)
    register_builtin_plugins(registry)
    register_plugin_pack(registry)
    register_extra_plugins(registry)
    return registry


@pytest.fixture()
def cache():
    return InMemoryCache()


@pytest.fixture()
def engine(repository, registry, cache):
    return WorkflowEngine(repository=repository, registry=registry, cache=cache)


@pytest.fixture()
def app(repository, registry, cache, engine):
    app = create_app()
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_registry] = lambda: registry
    app.dependency_overrides[get_cache] = lambda: cache
    app.dependency_overrides[get_engine] = lambda: engine
    return app
