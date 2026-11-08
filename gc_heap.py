from typing import Any, Dict, List, Tuple


class HeapNode:
    def __init__(self, **fields: Any) -> None:
        self.fields = fields

    def get_child_handles(self) -> List[int]:
        return [v for v in self.fields.values() if isinstance(v, int)]


class GCHeap:
    def __init__(self) -> None:
        self._slots: Dict[int, List[Any]] = {}
        self._next_handle = 1

    def allocate(self, obj: Any) -> int:
        handle = self._next_handle
        self._next_handle += 1
        self._slots[handle] = [obj, 1]
        return handle

    def incref(self, handle: int) -> None:
        if handle not in self._slots:
            raise ValueError(f"incref on dead or unknown handle {handle}")
        self._slots[handle][1] += 1

    def decref(self, handle: int) -> None:
        pending = [handle]
        while pending:
            h = pending.pop()
            slot = self._slots.get(h)
            if slot is None:
                raise ValueError(f"decref on dead or unknown handle {h}")
            slot[1] -= 1
            if slot[1] == 0:
                obj = slot[0]
                del self._slots[h]
                if hasattr(obj, "get_child_handles"):
                    pending.extend(obj.get_child_handles())

    def is_alive(self, handle: int) -> bool:
        return handle in self._slots

    def live_count(self) -> int:
        return len(self._slots)

    def refcount(self, handle: int) -> int:
        slot = self._slots.get(handle)
        return slot[1] if slot else 0