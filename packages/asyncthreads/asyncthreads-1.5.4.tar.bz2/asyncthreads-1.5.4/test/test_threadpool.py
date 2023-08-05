#
# Run with py.test
#
import pytest
import gc
import time
from random import randrange

# Uncomment to import from repo instead of site-packages.
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from asyncthreads import threadpool

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
        cls.pool = threadpool.ThreadPool(POOL_MIN, POOL_MAX)

    def test_create(self):
        with pytest.raises(ValueError) as e:
             bad_pool = threadpool.ThreadPool(0, 0)
        print('OK, caught: ' + str(e))

        with pytest.raises(ValueError) as e:
             bad_pool = threadpool.ThreadPool(-3, -7)
        print('OK, caught: ' + str(e))

        with pytest.raises(ValueError) as e:
             bad_pool = threadpool.ThreadPool(5, 2)
        print('OK, caught: ' + str(e))

        good_pool = threadpool.ThreadPool(5, -22)


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

        for _ in range(3):
            print('\n---> queued items: %s' % self.pool.qsize())
            print('---> idle threads: %s' % self.pool.idle_threads())
            print('---> thread count: %s' % self.pool.threads())
            time.sleep(2)

        assert self.pool.threads() <= POOL_MAX

        self.pool.resize_pool(80)
        assert self.pool.threads() == 80

        future = self.pool.submit(range, (0,1))
        while not future.done():
            print('\n---> queued items: %s' % self.pool.qsize())
            print('---> idle threads: %s' % self.pool.idle_threads())
            print('---> thread count: %s' % self.pool.threads())
            time.sleep(0.25)

        while True:
            self.pool.submit(range, (0,1))
            time.sleep(0.15)
            threads = self.pool.threads()
            idle = self.pool.idle_threads()
            print('\n---> queued items: %s' % self.pool.qsize())
            print('---> idle threads: %s' % idle)
            print('---> thread count: %s' % threads)
            if (threads == POOL_MIN and idle == self.pool.threads()):
                break

        print('finish')

    def test_map(self):
        results = self.pool.map(wait_task, range(1,6), task_callback)
        assert len(results) == 5
        print('Results:')
        for r in results:
            print(r)

        def square(i):
            return i * i

        def mul(i, j):
            return i * j

        pairs = [(2,3), (3,4), (4,5), (5,6)]
        results = self.pool.map(mul, pairs)
        assert len(pairs) == len(results)
        for i, r in enumerate(results):
            x,y = pairs[i]
            print("%s * %s = %s" % (x,y,r))
            assert r == x * y

        results = self.pool.map(square, range(5))
        assert len(results) == 5
        for i, r in enumerate(results):
            print("%s * %s = %s" % (i,i,r))
            assert r == i * i

        future = self.pool.map_async(mul, pairs)
        results = future.result()
        assert len(pairs) == len(results)
        for i, r in enumerate(results):
            x,y = pairs[i]
            print("%s * %s = %s" % (x,y,r))
            assert r == x * y

    def test_map_chunksize(self):
        """Test that concurrency of map() is limited by chunksize."""
        times = [3,3,2,2,1,1,3,1,2,2,1,3,1,2,3,3,2,1,3,1,2]
        pool = threadpool.ThreadPool(100, 100)
        chunksize = 5
        pool.map(wait_task, times, None, chunksize)
        print 'executed %s tasks with chunksize=%s, max pool size: %s' % (
            len(times), chunksize, pool.threads())
        # It is OK for there to be a few more threads than chunksize.  This
        # can happen if a task has completed by its thread has not yet been
        # marked idle before the next task arrives.
        assert pool.threads() <= chunksize + 3

    def test_shutdown(self):
        # When all tasks are finished, allow the threads to terminate
        print('Shutting down thread pool')

        # Shutdown, and wait for all threads to exit (default).
        self.pool.shutdown()

        with pytest.raises(RuntimeError) as e:
            self.pool.submit(wait_task, 10)

        assert not self.pool.shutdown()

        print('\n---> queued items: %s' % self.pool.qsize())
        print('---> idle threads: %s' % self.pool.idle_threads())
        print('---> thread count: %s' % self.pool.threads())
        assert self.pool.qsize() == 0
        assert self.pool.idle_threads() == 0
        assert self.pool.threads() == 0

    def test_memory_leaks(self):
        """Check for memory leaks"""
        # Test for any objects that cannot be freed.
        assert len(gc.garbage) == 0, 'uncollected garbage: '+str(gc.garbage)

