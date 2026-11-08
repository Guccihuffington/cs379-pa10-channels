import threading
from collections import deque
from typing import Any

from gc_heap import GCHeap

_CLOSED_SENTINEL = object()

class Channel:
    CLOSED = _CLOSED_SENTINEL

    def __init__(self, capacity: int, heap: GCHeap) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self._capacity = capacity
        self._heap = heap
        self._buffer: deque = deque()
        self._lock = threading.Lock()
        self._not_full = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)
        self._closed = False

    def put(self, value: Any) -> None:
        with self._lock:
            while len(self._buffer) >= self._capacity and not self._closed:
                self._not_full.wait()
            if self._closed:
                raise RuntimeError("put on closed channel")
            self._heap.incref(value) 
            self._buffer.append(value)
            self._not_empty.notify()

    def get(self) -> Any:
        with self._lock:
            while not self._buffer and not self._closed:
                self._not_empty.wait()
            if self._buffer:
                value = self._buffer.popleft()
                self._not_full.notify()
                return value
            return Channel.CLOSED

    def close(self) -> None:
        with self._lock:
            self._closed = True
            self._not_full.notify_all()
            self._not_empty.notify_all()


def _read_value(heap: GCHeap, handle: int) -> Any:
    for name in ("deref", "read", "value", "load", "get_object", "lookup", "get_value"):
        fn = getattr(heap, name, None)
        if callable(fn):
            return fn(handle)
    for attr in vars(heap).values():
        if isinstance(attr, dict) and handle in attr:
            entry = attr[handle]
            return entry[0] if isinstance(entry, (list, tuple)) else entry
    raise AttributeError("GCHeap has no recognizable accessor; edit _read_value")


def producer_consumer_driver(
    heap: GCHeap, values: list, channel: Channel, num_consumers: int = 1
):
    delivered: list = []
    delivered_lock = threading.Lock()

    def produce() -> None:
        try:
            for v in values:
                handle = heap.allocate(v)
                try:
                    channel.put(handle)
                finally:
                    heap.decref(handle)
        finally:
            channel.close()           

    def consume() -> None:
        while True:
            handle = channel.get()
            if not isinstance(handle, int):   
                return
            value = _read_value(heap, handle)
            with delivered_lock:
                delivered.append((handle, value))
            heap.decref(handle) 

    producer_thread = threading.Thread(target=produce)
    consumer_threads = [threading.Thread(target=consume) for _ in range(num_consumers)]
    for t in [producer_thread] + consumer_threads:
        t.start()
    producer_thread.join()
    for t in consumer_threads:
        t.join(timeout=10.0)

    return delivered