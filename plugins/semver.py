from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, raw: str) -> "Version":
        parts = raw.strip().split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version: {raw}")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]))

    def as_tuple(self) -> Tuple[int, int, int]:
        return (self.major, self.minor, self.patch)


def satisfies(version: str, constraint: str) -> bool:
    v = Version.parse(version)
    constraint = constraint.strip()

    if constraint.startswith("^"):
        base = Version.parse(constraint[1:])
        return v.major == base.major and v.as_tuple() >= base.as_tuple()
    if constraint.startswith("~"):
        base = Version.parse(constraint[1:])
        return v.major == base.major and v.minor == base.minor and v.as_tuple() >= base.as_tuple()
    if constraint.startswith(">="):
        base = Version.parse(constraint[2:])
        return v.as_tuple() >= base.as_tuple()
    if constraint.startswith("<="):
        base = Version.parse(constraint[2:])
        return v.as_tuple() <= base.as_tuple()
    if constraint.startswith(">"): 
        base = Version.parse(constraint[1:])
        return v.as_tuple() > base.as_tuple()
    if constraint.startswith("<"):
        base = Version.parse(constraint[1:])
        return v.as_tuple() < base.as_tuple()
    return v.as_tuple() == Version.parse(constraint).as_tuple()


def satisfies_any(version: str, constraints: Iterable[str]) -> bool:
    return any(satisfies(version, constraint) for constraint in constraints)
