import threading
from time import sleep, time
import unittest

from .. import ObjectPool, ObjectPoolTimeout

class TestOjbectPool(unittest.TestCase):

    def setUp(self):
        self.num_created = 0

    def _create(self):
        self.num_created += 1

    def _run_threads(self, target, num_threads):
        threads = [threading.Thread(target=target) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def test_create(self):
        pool = ObjectPool(self._create)
        self._run_threads(pool.get, 100)
        self.assertEqual(pool._size, 100)
        self.assertEqual(self.num_created, 100)

    def test_max_size(self):
        pool = ObjectPool(self._create, max_size=10)
        def get_and_put():
            item = pool.get()
            sleep(0.01)
            pool.put(item)
        self._run_threads(get_and_put, 100)
        self.assertGreater(pool._size, 0)
        self.assertLessEqual(pool._size, 10)
        self.assertGreater(self.num_created, 0)

    def test_blocking(self):
        pool = ObjectPool(self._create, max_size=1)
        item = pool.get()
        elapsed = []
        def get():
            begin = time()
            pool.get()
            elapsed.append(time() - begin)
        t = threading.Thread(target=get)
        t.start()
        sleep(0.01)
        pool.put(item)
        t.join()
        self.assertGreater(elapsed[0], 0.01)

    def test_timeout(self):
        pool = ObjectPool(self._create, max_size=1)
        item = pool.get()
        self.assertRaises(ObjectPoolTimeout, pool.get, timeout=0.01)
        pool.put(item)
        pool.get(timeout=0.0) # shouldn't raise

    def test_with(self):
        pool = ObjectPool(self._create, max_size=1)
        self.assertEqual(pool._size, 0)
        with pool.item():
            pass
        self.assertEqual(self.num_created, 1)
        self.assertEqual(len(pool._items), 1)
        self.assertEqual(pool._size, 1)
        try:
            with pool.item():
                raise RuntimeError
        except RuntimeError:
            pass
        self.assertEqual(self.num_created, 1)
        self.assertEqual(len(pool._items), 1)
        self.assertEqual(pool._size, 1)

if __name__ == '__main__':
    unittest.main()
