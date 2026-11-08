from typing import Any, List, Tuple
from parser import BinOp, Number, Variable
from symtable import Environment


class Cell:

    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value


class FunctionDecl:

    __slots__ = ("params", "body")

    def __init__(self, params: List[str], body) -> None:
        self.params = params
        self.body = body


def evaluate(node, env: Environment):
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Variable):
        val = env.resolve(node.name)
        return val.value if isinstance(val, Cell) else val
    if isinstance(node, BinOp):
        if node.op == "neg":
            return -evaluate(node.left, env)
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        return {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b}[node.op](left, right)
    raise ValueError(f"cannot evaluate node: {node!r}")


def assign_through(env: Environment, name: str, value: Any) -> None:
    cell = env.resolve(name)
    if not isinstance(cell, Cell):
        raise TypeError(f"'{name}' is not bound to a Cell -- did you forget to wrap it?")
    cell.value = value


def bind_parameters(param_specs: List[Tuple[str, str]], arg_nodes: list, caller_env: Environment, callee_record) -> None:
    if len(param_specs) != len(arg_nodes):
        raise TypeError(f"expected {len(param_specs)} arguments, got {len(arg_nodes)}")

    callee_env = callee_record.locals_env
    pending = []

    for (name, mode), node in zip(param_specs, arg_nodes):
        if mode == "value":
            callee_env.define(name, Cell(evaluate(node, caller_env)))

        elif mode in ("reference", "value-result"):
            if not isinstance(node, Variable):
                raise TypeError(f"'{mode}' parameter '{name}' needs a variable argument")
            caller_cell = caller_env.resolve(node.name)
            if not isinstance(caller_cell, Cell):
                raise TypeError(f"'{node.name}' is not bound to a Cell")

            if mode == "reference":
                callee_env.define(name, caller_cell)
            else:
                callee_env.define(name, Cell(caller_cell.value))
                pending.append((name, caller_cell))

        else:
            raise ValueError(f"unknown parameter mode: {mode!r}")

    callee_record.pending_writeback = pending


def commit_value_result(callee_record, caller_env: Environment) -> None:
    for name, caller_cell in getattr(callee_record, "pending_writeback", []):
        caller_cell.value = callee_record.locals_env.resolve(name).value


class Closure:
    def __init__(self, declaration: FunctionDecl, defining_env: Environment) -> None:
        self.declaration = declaration
        self.defining_env = defining_env

    def call(self, args: list, caller_env: Environment):
        params = self.declaration.params
        if len(args) != len(params):
            raise TypeError(f"expected {len(params)} arguments, got {len(args)}")

        env = Environment(self.defining_env)
        for name, value in zip(params, args):
            env.define(name, Cell(value))
        return evaluate(self.declaration.body, env)