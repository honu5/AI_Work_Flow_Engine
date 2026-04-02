from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class CapabilityRequirement:
    name: str
    value: str | None = None


@dataclass
class PluginCapabilities:
    items: List[str]

    def supports(self, requirement: CapabilityRequirement) -> bool:
        if requirement.value is None:
            return requirement.name in self.items
        return f"{requirement.name}:{requirement.value}" in self.items

    def supports_all(self, requirements: Iterable[CapabilityRequirement]) -> bool:
        return all(self.supports(req) for req in requirements)
