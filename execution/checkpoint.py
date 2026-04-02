from __future__ import annotations

from typing import Any, Dict, List, Optional

from storage.repository import Repository
from utils.ids import new_id


class CheckpointManager:
    """Persists partial execution output for inspection and resume planning."""

    def __init__(self, repository: Repository) -> None:
        self._repository = repository

    def save(
        self,
        execution_id: str,
        node_id: str,
        status: str,
        outputs: Dict[str, Any],
    ) -> str:
        checkpoint_id = new_id("chk")
        self._repository.save_execution_checkpoint(
            checkpoint_id=checkpoint_id,
            execution_id=execution_id,
            node_id=node_id,
            status=status,
            outputs=outputs,
        )
        return checkpoint_id

    def latest_for_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        checkpoints = self._repository.list_execution_checkpoints(execution_id)
        return checkpoints[-1] if checkpoints else None

    def list_for_execution(self, execution_id: str) -> List[Dict[str, Any]]:
        return self._repository.list_execution_checkpoints(execution_id)

    def outputs_snapshot(self, execution_id: str) -> Dict[str, Any]:
        latest = self.latest_for_execution(execution_id)
        if latest is None:
            return {}
        return latest.get("outputs", {})
