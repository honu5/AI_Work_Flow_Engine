from __future__ import annotations

from typing import Any, Callable, Dict

from workflows.expressions.ast import Binary, Call, Expr, Identifier, Number, Unary
from workflows.expressions.errors import ExpressionError


class Evaluator:
    def __init__(self, context: Dict[str, Any], functions: Dict[str, Callable[..., Any]] | None = None) -> None:
        self._context = context
        self._functions = functions or {}

    def evaluate(self, expr: Expr) -> Any:
        if isinstance(expr, Number):
            return expr.value
        if isinstance(expr, Identifier):
            if expr.name not in self._context:
                raise ExpressionError(f"Unknown identifier {expr.name}")
            return self._context[expr.name]
        if isinstance(expr, Unary):
            value = self.evaluate(expr.value)
            return -value if expr.op == "-" else value
        if isinstance(expr, Binary):
            return self._apply_binary(expr.op, self.evaluate(expr.left), self.evaluate(expr.right))
        if isinstance(expr, Call):
            if expr.name not in self._functions:
                raise ExpressionError(f"Unknown function {expr.name}")
            return self._functions[expr.name](*[self.evaluate(arg) for arg in expr.args])
        raise ExpressionError("Unknown expression")

    def _apply_binary(self, op: str, left: Any, right: Any) -> Any:
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left / right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        if op == "==":
            return left == right
        raise ExpressionError(f"Unknown operator {op}")
