from workflows.expressions.evaluator import Evaluator
from workflows.expressions.parser import ExpressionParser
from workflows.expressions.stdlib import build_default_functions


def test_stdlib_avg_function():
    expr = ExpressionParser("avg(2, 4, 6)").parse()
    result = Evaluator({}, build_default_functions()).evaluate(expr)
    assert result == 4.0


def test_stdlib_between_function():
    expr = ExpressionParser("between(5, 1, 10)").parse()
    result = Evaluator({}, build_default_functions()).evaluate(expr)
    assert result is True
