from typing import Dict, List, Optional
from symtable import Environment
class ActivationRecord:
    def __init__(
        self,
        function_name: str,
        parameters: Dict[str, object],
        locals_env: Environment,
        return_address: str,
        static_link: Optional["ActivationRecord"],
        dynamic_link: Optional["ActivationRecord"],
    ) -> None:
        self.function_name = function_name
        self.parameters = parameters
        self.locals_env = locals_env
        self.return_address = return_address
        self.static_link = static_link
        self.dynamic_link = dynamic_link

    def __repr__(self) -> str:
        params = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        dyn = self.dynamic_link.function_name if self.dynamic_link else None
        sta = self.static_link.function_name if self.static_link else None
        return (f"{self.function_name}({params}) "
                f"ret={self.return_address} dynamic={dyn} static={sta}")


class CallStack:
    def __init__(self) -> None:
        self._frames: List[ActivationRecord] = []

    def push(self, record: ActivationRecord) -> None:
        self._frames.append(record)

    def pop(self) -> ActivationRecord:
        if not self._frames:
            raise IndexError("pop from empty call stack")
        return self._frames.pop()

    def current(self) -> ActivationRecord:
        if not self._frames:
            raise IndexError("call stack is empty")
        return self._frames[-1]

    def __len__(self) -> int:
        return len(self._frames)

    def trace(self) -> List[str]:
        return [f"#{i} {frame!r}" for i, frame in enumerate(self._frames)]