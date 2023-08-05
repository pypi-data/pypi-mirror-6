from contextlib import contextmanager
import threading
from time import time

__version__ = 0.1

class ObjectPoolTimeout(RuntimeError):
    pass

class ObjectPool(object):

    def __init__(self, create, max_size=None):
        self._create = create
        self._max_size = max_size
        self._size = 0
        self._items = []
        self._mutex = threading.Lock()
        self._item_available = threading.Condition(self._mutex)

    def get(self, timeout=None):
        with self._mutex:
            if not self._items and (self._max_size is None or self._size < self._max_size):
                item = self._create()
                self._size += 1
            else:
                if timeout is not None:
                    end = time() + timeout
                while not self._items:
                    remaining = timeout
                    if timeout is not None:
                        remaining = end - time()
                        if remaining <= 0.0:
                            raise ObjectPoolTimeout
                    self._item_available.wait(remaining)
                item = self._items.pop()
        return item

    def put(self, item):
        with self._mutex:
            self._items.append(item)
            self._item_available.notify()

    @contextmanager
    def item(self):
        item = self.get()
        try:
            yield item
        finally:
            self.put(item)
