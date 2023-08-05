#
# Run with py.test
#
import pytest
import gc
import time
from random import randrange

# Uncomment to import from repo instead of site-packages.
#import os
#import sys
#parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.insert(0, parentdir)

from asyncthreads import threadrunner

# Sample task 1: given a start and end value, shuffle integers,
# then sort them
def sort_task(first, last):
    print("SortTask starting for %s" % ((first, last),))
    numbers = list(range(first, last))
    for a in numbers:
        rnd = randrange(0, len(numbers) - 1)
        a, numbers[rnd] = numbers[rnd], a
    print("SortTask sorting for %s" % ((first, last),))
    numbers.sort()
    print("SortTask done for %s" % ((first, last),))
    return ("Sorter ", (first, last))

# Sample task 2: just sleep for a number of seconds.
def wait_task(data):
    print("WaitTask starting for %s" % (data,))
    print("WaitTask sleeping for %d seconds" % (data,))
    time.sleep(data)
    return "Waiter", data

# Both tasks use the same callback
def task_callback(data):
    print("Callback called for %s" % (data,))
    pass

POOL_MIN = 4
POOL_MAX = 24

class TestThreadPool(object):

    @classmethod
    def setup_class(cls):
        gc.set_debug(gc.DEBUG_UNCOLLECTABLE)
        cls.pool = threadrunner.ThreadRunner()

    def test_start(self):
        for _ in range(50):
            self.pool.submit(wait_task, 15, task_callback)

        # Insert tasks into the queue and let them run
        print('start')
        self.pool.submit(sort_task, (1000, 100000), task_callback)
        self.pool.submit(wait_task, 5, task_callback)
        self.pool.submit(sort_task, (200, 200000), task_callback)
        self.pool.submit(wait_task, 2, task_callback)
        self.pool.submit(sort_task, (3, 30000), task_callback)
        self.pool.submit(wait_task, 7, task_callback)
        self.pool.submit(sort_task, (1000, 100000), task_callback)
        self.pool.submit(wait_task, 5, task_callback)
        self.pool.submit(sort_task, (200, 200000), task_callback)
        self.pool.submit(wait_task, 2, task_callback)
        self.pool.submit(sort_task, (3, 30000), task_callback)
        self.pool.submit(wait_task, 7, task_callback)
        self.pool.submit(sort_task, (201, 200001), task_callback)
        self.pool.submit(sort_task, (202, 200002), task_callback)
        self.pool.submit(sort_task, (203, 200003), task_callback)
        self.pool.submit(sort_task, (204, 200004), task_callback)
        self.pool.submit(sort_task, (205, 200005), task_callback)
        self.pool.submit(sort_task, (1000, 100000), task_callback)
        self.pool.submit(wait_task, 5, task_callback)
        self.pool.submit(sort_task, (200, 200000), task_callback)
        self.pool.submit(wait_task, 2, task_callback)
        self.pool.submit(sort_task, (3, 30000), task_callback)
        self.pool.submit(wait_task, 7, task_callback)
        self.pool.submit(sort_task, (1000, 100000), task_callback)
        self.pool.submit(wait_task, 5, task_callback)
        self.pool.submit(sort_task, (200, 200000), task_callback)
        self.pool.submit(wait_task, 2, task_callback)
        self.pool.submit(sort_task, (3, 30000), task_callback)
        self.pool.submit(wait_task, 7, task_callback)
        self.pool.submit(sort_task, (201, 200001), task_callback)
        self.pool.submit(sort_task, (202, 200002), task_callback)
        self.pool.submit(sort_task, (203, 200003), task_callback)
        self.pool.submit(sort_task, (204, 200004), task_callback)
        self.pool.submit(sort_task, (205, 200005), task_callback)

        future = self.pool.submit(wait_task, 17, task_callback)
        while not future.done():
            print('\n---> waiting for 17 second wait task')
            time.sleep(0.25)

        print('finish')

    def test_map(self):
        results = self.pool.map(wait_task, range(1,6), task_callback)
        assert len(results) == 5
        print('Results:')
        for r in results:
            print(r)

    def test_shutdown(self):
        # When all tasks are finished, allow the threads to terminate
        print('Shutting down thread pool')

        # Shutdown, and wait for all threads to exit (default).
        self.pool.shutdown()

        with pytest.raises(RuntimeError) as e:
            self.pool.submit(wait_task, 10)

        assert not self.pool.shutdown()

    def test_memory_leaks(self):
        """Check for memory leaks"""
        # Test for any objects that cannot be freed.
        assert len(gc.garbage) == 0, 'uncollected garbage: '+str(gc.garbage)

