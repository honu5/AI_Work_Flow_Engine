from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class Token:
    kind: str
    value: str


class Lexer:
    def __init__(self, text: str) -> None:
        self._text = text
        self._index = 0

    def tokenize(self) -> Iterator[Token]:
        while self._index < len(self._text):
            ch = self._text[self._index]
            if ch.isspace():
                self._index += 1
                continue
            if ch.isdigit():
                yield self._read_number()
                continue
            if ch.isalpha() or ch == "_":
                yield self._read_ident()
                continue
            if ch in "()+-*/<>=" or ch == ",":
                yield self._read_operator()
                continue
            raise ValueError(f"Unexpected character {ch}")
        yield Token("EOF", "")

    def _read_number(self) -> Token:
        start = self._index
        while self._index < len(self._text) and (
            self._text[self._index].isdigit() or self._text[self._index] == "."
        ):
            self._index += 1
        return Token("NUMBER", self._text[start:self._index])

    def _read_ident(self) -> Token:
        start = self._index
        while self._index < len(self._text) and (
            self._text[self._index].isalnum() or self._text[self._index] == "_"
        ):
            self._index += 1
        return Token("IDENT", self._text[start:self._index])

    def _read_operator(self) -> Token:
        ch = self._text[self._index]
        self._index += 1
        if ch in ("<", ">", "=") and self._index < len(self._text):
            nxt = self._text[self._index]
            if nxt == "=":
                self._index += 1
                return Token("OP", ch + nxt)
        return Token("OP", ch)
