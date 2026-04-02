from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from plugins.base import Plugin


@dataclass(frozen=True)
class PluginManifest:
    name: str
    version: str
    description: str
    module: str
    class_name: str
    capabilities: List[str]


def load_manifests(directory: Path) -> List[PluginManifest]:
    manifests: List[PluginManifest] = []
    for file_path in directory.glob("*.json"):
        data = json.loads(file_path.read_text(encoding="utf-8"))
        manifests.append(
            PluginManifest(
                name=data["name"],
                version=data["version"],
                description=data.get("description", ""),
                module=data["module"],
                class_name=data["class"],
                capabilities=data.get("capabilities", []),
            )
        )
    return manifests


def instantiate_plugins(manifests: Iterable[PluginManifest]) -> List[Plugin]:
    plugins: List[Plugin] = []
    for manifest in manifests:
        module = importlib.import_module(manifest.module)
        plugin_class = getattr(module, manifest.class_name)
        plugins.append(plugin_class())
    return plugins
