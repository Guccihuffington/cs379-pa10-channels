from dataclasses import dataclass, field
from typing import List
from lexer import Token, tokenize
@dataclass
class Program:
    statements: list
@dataclass
class Declaration:
    name: str
    expr: object
    line: int
@dataclass
class Assignment:
    name: str
    expr: object
    line: int
@dataclass
class BinOp:
    op: str
    left: object
    right: object
    line: int
@dataclass
class Number:
    value: int
    line: int
@dataclass
class Variable:
    name: str
    line: int
class ParseError(Exception):
    pass
class _ParserState:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, type_: str) -> Token:
        tok = self.peek()
        if tok.type != type_:
            raise ParseError(f"Line {tok.line}: expected {type_}, found {tok.type} ({tok.lexeme!r}).")
        return self.advance()
    def check(self, type_: str) -> bool:
        return self.peek().type == type_

def parse_factor(state: _ParserState):
    tok = state.peek()

    if tok.type == "NUMBER":
        state.advance()
        return Number(value=int(tok.lexeme), line=tok.line)

    if tok.type == "IDENT":
        state.advance()
        return Variable(name=tok.lexeme, line=tok.line)

    if tok.type == "LPAREN":
        state.advance()
        expr = parse_expr(state)
        state.expect("RPAREN")
        return expr

    raise ParseError(f"Line {tok.line}: expected NUMBER, IDENT, or '(', found {tok.type} ({tok.lexeme!r}).")

def parse_term(state: _ParserState):
    node = parse_factor(state)

    while state.peek().type in ("STAR", "SLASH"):
        op_tok = state.advance()
        op = "*" if op_tok.type == "STAR" else "/"
        right = parse_factor(state)
        node = BinOp(op=op, left=node, right=right, line=op_tok.line)

    return node

def parse_expr(state: _ParserState):
    node = parse_term(state)

    while state.peek().type in ("PLUS", "MINUS"):
        op_tok = state.advance()
        op = "+" if op_tok.type == "PLUS" else "-"
        right = parse_term(state)
        node = BinOp(op=op, left=node, right=right, line=op_tok.line)

    return node

def parse_declaration(state: _ParserState) -> Declaration:
    let_tok = state.expect("LET")
    name_tok = state.expect("IDENT")
    state.expect("ASSIGN")
    expr = parse_expr(state)
    state.expect("SEMI")
    return Declaration(name=name_tok.lexeme, expr=expr, line=let_tok.line)

def parse_assignment(state: _ParserState) -> Assignment:
    name_tok = state.expect("IDENT")
    state.expect("ASSIGN")
    expr = parse_expr(state)
    state.expect("SEMI")
    return Assignment(name=name_tok.lexeme, expr=expr, line=name_tok.line)

def parse_statement(state: _ParserState):
    tok = state.peek()

    if tok.type == "LET":
        return parse_declaration(state)

    if tok.type == "IDENT":
        return parse_assignment(state)

    raise ParseError(f"Line {tok.line}: expected 'let' or identifier, found {tok.type} ({tok.lexeme!r}).")

def parse_program(state: _ParserState) -> Program:
    statements = []
    while not state.check("EOF"):
        statements.append(parse_statement(state))
    return Program(statements=statements)

def parse(tokens: List[Token]) -> Program:
    state = _ParserState(tokens)
    return parse_program(state)

