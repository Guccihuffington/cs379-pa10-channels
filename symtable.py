from typing import Optional, Any
from parser import Assignment, BinOp, Declaration, Number, Program, Variable

class SemanticError(Exception):
    pass
class Environment:
    def __init__(self, parent: Optional["Environment"] = None) -> None:
        self.parent = parent
        self._names: dict[str, Any] = {}

    @staticmethod
    def _describe(value: Any) -> str:
        return f"line {value}" if isinstance(value, int) else "an earlier declaration"

    def define(self, name: str, value: Any) -> None:
        if name in self._names:
            raise SemanticError(
                f"Duplicate declaration of '{name}' "
                f"({self._describe(value)}; originally declared at {self._describe(self._names[name])})."
            )
        self._names[name] = value

    def resolve(self, name: str) -> Any:
        env: Optional["Environment"] = self
        while env is not None:
            if name in env._names:
                return env._names[name]
            env = env.parent
        raise SemanticError(f"Use of undeclared variable '{name}'.")

def _resolve_at(env: Environment, name: str, line: int) -> int:
    try:
        return env.resolve(name)
    except SemanticError:
        raise SemanticError(
            f"Use of undeclared variable '{name}' (line {line})."
        )
    
def _check_expr(env: Environment, expr) -> None:
    if isinstance(expr, Variable):
        _resolve_at(env, expr.name, expr.line)
    elif isinstance(expr, BinOp):
        _check_expr(env, expr.left)
        _check_expr(env, expr.right)
    elif isinstance(expr, Number):
        pass
    else:
        pass

def check_program(ast: Program) -> Environment:
    global_env = Environment(parent=None)

    for stmt in ast.statements:
        if isinstance(stmt, Declaration):
            _check_expr(global_env, stmt.expr)
            global_env.define(stmt.name, stmt.line)

        elif isinstance(stmt, Assignment):
            _resolve_at(global_env, stmt.name, stmt.line)
            _check_expr(global_env, stmt.expr)

        else:
            raise SemanticError(
                f"Unknown statement type: {type(stmt).__name__}"
            )

    return global_env