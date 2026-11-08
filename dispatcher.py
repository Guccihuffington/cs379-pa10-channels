from typing import Dict, Optional, Protocol
class MethodLike(Protocol):
    def call(self, args: list, caller_env) -> object:
        """PA 7 Closure-compatible call interface."""


class ClassDecl:

    __slots__ = ("name", "methods")

    def __init__(self, name: str, methods: Dict[str, MethodLike]) -> None:
        self.name = name
        self.methods = methods  # methods declared on THIS class only


class VTable:
    def __init__(self, entries: Dict[str, MethodLike], owning_class_name: str = "?") -> None:
        self.entries = entries
        self.owning_class_name = owning_class_name

    def resolve(self, method_name: str) -> MethodLike:
        try:
            return self.entries[method_name]
        except KeyError:
            raise AttributeError(
                f"Class '{self.owning_class_name}' has no method '{method_name}'"
            ) from None


def build_vtable(class_node: ClassDecl, parent_vtable: Optional[VTable] = None) -> VTable:
    # New dict, same method objects: inherited slots are shared, not duplicated.
    entries = dict(parent_vtable.entries) if parent_vtable is not None else {}
    # Overwrite only the slots this class redeclares.
    entries.update(class_node.methods)
    return VTable(entries, owning_class_name=class_node.name)


class USIObject:
    def __init__(self, class_descriptor: VTable, fields: dict) -> None:
        self.class_descriptor = class_descriptor  # the ACTUAL runtime class's VTable
        self.fields = fields


def dispatch(obj: USIObject, method_name: str, args: list, caller_env) -> object:
    method = obj.class_descriptor.resolve(method_name)  # never a declared/static type
    return method.call([obj, *args], caller_env)         # obj is the receiver/self