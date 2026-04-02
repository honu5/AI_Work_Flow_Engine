import json
from pathlib import Path

from plugins.discovery import instantiate_plugins, load_manifests


def test_discovery_loads_manifests(tmp_path: Path):
    manifest = {
        "name": "echo",
        "version": "1.0.0",
        "description": "Echo",
        "module": "plugins.builtin",
        "class": "EchoPlugin",
        "capabilities": ["core:echo"],
    }
    (tmp_path / "echo.json").write_text(json.dumps(manifest), encoding="utf-8")

    manifests = load_manifests(tmp_path)
    assert manifests[0].name == "echo"

    plugins = instantiate_plugins(manifests)
    assert plugins[0].name == "echo"
