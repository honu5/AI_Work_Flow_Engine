from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from plugins.registry import PluginRegistry
from storage.db import init_db
from storage.repository import Repository
from workflows.catalog.loader import load_catalog
from workflows.linter import WorkflowLinter


def run_doctor(project_root: Path | None = None) -> Dict[str, Any]:
    root = project_root or Path(__file__).resolve().parents[1]
    report: Dict[str, Any] = {"checks": [], "ok": True}

    def add(name: str, ok: bool, detail: str) -> None:
        report["checks"].append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            report["ok"] = False

    catalog_dir = root / "workflows" / "catalog"
    if catalog_dir.exists():
        templates = load_catalog(catalog_dir)
        add("catalog", len(templates) >= 10, f"{len(templates)} templates")
    else:
        add("catalog", False, "catalog directory missing")

    try:
        init_db(force=True, database_url="sqlite:///:memory:")
        repository = Repository()
        registry = PluginRegistry(repository)
        from plugins.builtin import register_builtin_plugins
        from plugins.pack import register_plugin_pack

        register_builtin_plugins(registry)
        register_plugin_pack(registry)
        add("plugins", len(registry.list_plugins()) > 20, f"{len(registry.list_plugins())} plugins")
    except Exception as exc:  # noqa: BLE001
        add("plugins", False, str(exc))

    linter = WorkflowLinter()
    sample = load_catalog(catalog_dir)[0] if catalog_dir.exists() else None
    if sample is not None:
        lint = linter.lint(sample.nodes)
        add("linter", lint.ok(), f"{lint.error_count} errors, {lint.warning_count} warnings")

    return report
