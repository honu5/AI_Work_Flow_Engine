#!/usr/bin/env python3
"""Export programmatic scenarios to JSON files for inspection."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from workflows.scenarios import list_scenario_builders
from workflows.scenarios.builders import build_scenario


def main() -> None:
    out_dir = ROOT / "workflows" / "catalog" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in list_scenario_builders():
        workflow = build_scenario(name)
        path = out_dir / f"{name}.json"
        path.write_text(json.dumps([workflow.model_dump()], indent=2), encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
