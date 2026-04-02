from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator, List


class TokenKind(str, Enum):
    WORKFLOW = "WORKFLOW"
    NODE = "NODE"
    PLUGIN = "PLUGIN"
    DEPENDS = "DEPENDS"
    IDENT = "IDENT"
    STRING = "STRING"
    NUMBER = "NUMBER"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    COLON = "COLON"
    COMMA = "COMMA"
    EOF = "EOF"


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: str
    line: int
    column: int


class WorkflowLexer:
    KEYWORDS = {
        "workflow": TokenKind.WORKFLOW,
        "node": TokenKind.NODE,
        "plugin": TokenKind.PLUGIN,
        "depends": TokenKind.DEPENDS,
    }

    def __init__(self, text: str) -> None:
        self._text = text
        self._pos = 0
        self._line = 1
        self._column = 1

    def tokenize(self) -> Iterator[Token]:
        while self._pos < len(self._text):
            ch = self._text[self._pos]
            if ch.isspace():
                self._advance()
                continue
            if ch == "#":
                while self._pos < len(self._text) and self._text[self._pos] != "\n":
                    self._advance()
                continue
            if ch in "{}":
                kind = TokenKind.LBRACE if ch == "{" else TokenKind.RBRACE
                yield self._emit(kind, ch)
                self._advance()
                continue
            if ch in ":,":
                kind = TokenKind.COLON if ch == ":" else TokenKind.COMMA
                yield self._emit(kind, ch)
                self._advance()
                continue
            if ch in "\"'":
                yield self._read_string(ch)
                continue
            if ch.isdigit() or (ch == "-" and self._peek_digit()):
                yield self._read_number()
                continue
            if ch.isalpha() or ch == "_":
                yield self._read_ident()
                continue
            raise SyntaxError(f"Unexpected character {ch!r} at {self._line}:{self._column}")
        yield self._emit(TokenKind.EOF, "")

    def _peek_digit(self) -> bool:
        return self._pos + 1 < len(self._text) and self._text[self._pos + 1].isdigit()

    def _read_string(self, quote: str) -> Token:
        start_line, start_col = self._line, self._column
        self._advance()
        buf: List[str] = []
        while self._pos < len(self._text):
            ch = self._text[self._pos]
            if ch == quote:
                self._advance()
                return Token(TokenKind.STRING, "".join(buf), start_line, start_col)
            if ch == "\\" and self._pos + 1 < len(self._text):
                self._advance()
                buf.append(self._text[self._pos])
                self._advance()
                continue
            buf.append(ch)
            self._advance()
        raise SyntaxError(f"Unterminated string at {start_line}:{start_col}")

    def _read_number(self) -> Token:
        start_line, start_col = self._line, self._column
        buf: List[str] = []
        if self._text[self._pos] == "-":
            buf.append("-")
            self._advance()
        while self._pos < len(self._text) and (self._text[self._pos].isdigit() or self._text[self._pos] == "."):
            buf.append(self._text[self._pos])
            self._advance()
        return Token(TokenKind.NUMBER, "".join(buf), start_line, start_col)

    def _read_ident(self) -> Token:
        start_line, start_col = self._line, self._column
        buf: List[str] = []
        while self._pos < len(self._text) and (self._text[self._pos].isalnum() or self._text[self._pos] in "._-"):
            buf.append(self._text[self._pos])
            self._advance()
        raw = "".join(buf)
        kind = self.KEYWORDS.get(raw, TokenKind.IDENT)
        return Token(kind, raw, start_line, start_col)

    def _advance(self) -> None:
        if self._pos < len(self._text) and self._text[self._pos] == "\n":
            self._line += 1
            self._column = 1
        else:
            self._column += 1
        self._pos += 1

    def _emit(self, kind: TokenKind, value: str) -> Token:
        return Token(kind, value, self._line, self._column)
