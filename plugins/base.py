from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class Plugin(ABC):
    name: str
    version: str
    description: str

    @abstractmethod
    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
