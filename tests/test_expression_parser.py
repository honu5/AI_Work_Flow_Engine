import pytest

from workflows.expressions.parser import ExpressionParser


def test_expression_parser_parses_math():
    expr = ExpressionParser("1 + 2 * 3").parse()
    assert expr is not None


def test_expression_parser_parses_call():
    expr = ExpressionParser("sum(1, 2, 3)").parse()
    assert expr is not None


def test_expression_parser_rejects_trailing():
    with pytest.raises(Exception):
        ExpressionParser("1 1").parse()
