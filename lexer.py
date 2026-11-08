import re
from dataclasses import dataclass
from typing import List
@dataclass
class Token:
    type: str
    lexeme: str
    line: int

class LexError(Exception):
    pass

_KEYWORDS = {
    "let": "LET",
}
_MASTER_RE = re.compile(
    r"(?P<SKIP>[ \t]+)"
    r"|(?P<NEWLINE>\n)"
    r"|(?P<COMMENT>\#[^\n]*)"
    r"|(?P<NUMBER>\d+(?:\.\d+)?)"
    r"|(?P<IDENT>[A-Za-z_]\w*)"
    r"|(?P<ASSIGN>=)"
    r"|(?P<PLUS>\+)"
    r"|(?P<MINUS>-)"
    r"|(?P<STAR>\*)"
    r"|(?P<SLASH>/)"
    r"|(?P<LPAREN>\()"
    r"|(?P<RPAREN>\))"
    r"|(?P<SEMI>;)"
)

_DISCARD = {"SKIP", "NEWLINE", "COMMENT"}

def tokenize(source: str) -> List[Token]:

    tokens: List[Token] = []
    pos = 0
    line = 1
    n = len(source)

    while pos < n:
        match = _MASTER_RE.match(source, pos)
        if match is None:
            raise LexError(
                f"Unexpected character {source[pos]!r} on line {line}"
            )

        kind = match.lastgroup
        if kind is None:
            raise LexError(f"Internal lexer error: no token type matched on line {line}")
        lexeme = match.group()

        if kind == "NEWLINE":
            line += 1
            pos = match.end()
            continue

        if kind in _DISCARD:
            pos = match.end()
            continue

        if kind == "IDENT":
            kind = _KEYWORDS.get(lexeme, "IDENT")

        tokens.append(Token(kind, lexeme, line))
        pos = match.end()

    tokens.append(Token("EOF", "", line))
    return tokens
 
 
if __name__ == "__main__":
    demo = "let x = 3 + 4 * (y - 1); # comment\nlet letter = x / 2;"
    for tok in tokenize(demo):
        print(tok)
 
    # TODO
    raise NotImplementedError
