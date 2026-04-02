from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List


class Expr:
    pass


@dataclass
class Number(Expr):
    value: float


@dataclass
class Identifier(Expr):
    name: str


@dataclass
class Binary(Expr):
    op: str
    left: Expr
    right: Expr


@dataclass
class Unary(Expr):
    op: str
    value: Expr


@dataclass
class Call(Expr):
    name: str
    args: List[Expr]
