from __future__ import annotations

from typing import List

from workflows.expressions.ast import Binary, Call, Expr, Identifier, Number, Unary
from workflows.expressions.errors import ExpressionError
from workflows.expressions.tokens import Lexer, Token


class ExpressionParser:
    def __init__(self, text: str) -> None:
        self._tokens: List[Token] = list(Lexer(text).tokenize())
        self._index = 0

    def parse(self) -> Expr:
        expr = self._parse_expression()
        if self._peek().kind != "EOF":
            raise ExpressionError("Unexpected trailing tokens")
        return expr

    def _parse_expression(self) -> Expr:
        return self._parse_comparison()

    def _parse_comparison(self) -> Expr:
        expr = self._parse_term()
        while self._peek().value in ("<", "<=", ">", ">=", "=="):
            op = self._advance().value
            right = self._parse_term()
            expr = Binary(op=op, left=expr, right=right)
        return expr

    def _parse_term(self) -> Expr:
        expr = self._parse_factor()
        while self._peek().value in ("+", "-"):
            op = self._advance().value
            right = self._parse_factor()
            expr = Binary(op=op, left=expr, right=right)
        return expr

    def _parse_factor(self) -> Expr:
        expr = self._parse_unary()
        while self._peek().value in ("*", "/"):
            op = self._advance().value
            right = self._parse_unary()
            expr = Binary(op=op, left=expr, right=right)
        return expr

    def _parse_unary(self) -> Expr:
        if self._peek().value in ("+", "-"):
            op = self._advance().value
            return Unary(op=op, value=self._parse_unary())
        return self._parse_primary()

    def _parse_primary(self) -> Expr:
        token = self._peek()
        if token.kind == "NUMBER":
            self._advance()
            return Number(float(token.value))
        if token.kind == "IDENT":
            self._advance()
            if self._peek().value == "(":
                return self._parse_call(token.value)
            return Identifier(token.value)
        if token.value == "(":
            self._advance()
            expr = self._parse_expression()
            self._expect(")")
            return expr
        raise ExpressionError("Unexpected token")

    def _parse_call(self, name: str) -> Expr:
        self._expect("(")
        args: List[Expr] = []
        if self._peek().value != ")":
            args.append(self._parse_expression())
            while self._peek().value == ",":
                self._advance()
                args.append(self._parse_expression())
        self._expect(")")
        return Call(name=name, args=args)

    def _peek(self) -> Token:
        return self._tokens[self._index]

    def _advance(self) -> Token:
        token = self._tokens[self._index]
        self._index += 1
        return token

    def _expect(self, value: str) -> None:
        token = self._advance()
        if token.value != value:
            raise ExpressionError(f"Expected {value}")
