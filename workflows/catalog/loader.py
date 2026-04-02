from __future__ import annotations

import json
from pathlib import Path
from typing import List

from workflows.schema import WorkflowCreate


def load_catalog(directory: Path) -> List[WorkflowCreate]:
    templates: List[WorkflowCreate] = []
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in data:
            templates.append(WorkflowCreate(**entry))
    return templates
#####