import pytest

from workflows.expressions.evaluator import Evaluator
from workflows.expressions.parser import ExpressionParser


def test_expression_evaluator_math():
    expr = ExpressionParser("1 + 2 * 3").parse()
    result = Evaluator({}).evaluate(expr)
    assert result == 7


def test_expression_evaluator_function_call():
    expr = ExpressionParser("add(1, 2, 3)").parse()
    result = Evaluator({}, {"add": lambda *values: sum(values)}).evaluate(expr)
    assert result == 6


def test_expression_evaluator_identifier():
    expr = ExpressionParser("x + 1").parse()
    result = Evaluator({"x": 4}).evaluate(expr)
    assert result == 5
