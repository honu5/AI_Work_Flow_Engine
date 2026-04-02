from __future__ import annotations

from typing import Any, List

from workflows.dsl.ast_nodes import InputBlock, NodeDecl, WorkflowDecl
from workflows.dsl.tokens import Token, TokenKind, WorkflowLexer


class WorkflowDslParser:
    def __init__(self, text: str) -> None:
        self._tokens: List[Token] = list(WorkflowLexer(text).tokenize())
        self._index = 0

    def parse(self) -> WorkflowDecl:
        self._expect(TokenKind.WORKFLOW)
        name = self._expect(TokenKind.IDENT).value
        self._expect(TokenKind.LBRACE)
        nodes: List[NodeDecl] = []
        while self._peek().kind != TokenKind.RBRACE:
            nodes.append(self._parse_node())
        self._expect(TokenKind.RBRACE)
        self._expect(TokenKind.EOF)
        return WorkflowDecl(name=name, nodes=nodes)

    def _parse_node(self) -> NodeDecl:
        self._expect(TokenKind.NODE)
        node_id = self._expect(TokenKind.IDENT).value
        self._expect(TokenKind.PLUGIN)
        plugin = self._expect(TokenKind.IDENT).value
        input_block = self._parse_input_block()
        depends: List[str] = []
        if self._peek().kind == TokenKind.DEPENDS:
            self._advance()
            depends.append(self._expect(TokenKind.IDENT).value)
            while self._peek().kind == TokenKind.IDENT:
                depends.append(self._advance().value)
        return NodeDecl(node_id=node_id, plugin=plugin, input_block=input_block, depends_on=depends)

    def _parse_input_block(self) -> InputBlock:
        self._expect(TokenKind.LBRACE)
        values: dict[str, Any] = {}
        while self._peek().kind != TokenKind.RBRACE:
            key = self._expect(TokenKind.IDENT).value
            self._expect(TokenKind.COLON)
            values[key] = self._parse_value()
            if self._peek().kind == TokenKind.COMMA:
                self._advance()
        self._expect(TokenKind.RBRACE)
        return InputBlock(values=values)

    def _parse_value(self) -> Any:
        token = self._peek()
        if token.kind == TokenKind.STRING:
            self._advance()
            return token.value
        if token.kind == TokenKind.NUMBER:
            self._advance()
            return float(token.value) if "." in token.value else int(token.value)
        if token.kind == TokenKind.IDENT:
            self._advance()
            if token.value in ("true", "false"):
                return token.value == "true"
            return token.value
        raise SyntaxError(f"Unexpected value token {token.kind} at {token.line}:{token.column}")

    def _peek(self) -> Token:
        return self._tokens[self._index]

    def _advance(self) -> Token:
        token = self._tokens[self._index]
        self._index += 1
        return token

    def _expect(self, kind: TokenKind) -> Token:
        token = self._peek()
        if token.kind != kind:
            raise SyntaxError(f"Expected {kind}, got {token.kind} at {token.line}:{token.column}")
        return self._advance()
