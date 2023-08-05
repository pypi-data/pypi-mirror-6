#
# Run with py.test
#

import pytest
import string
import gc
import time
import threading
try:
    import queue
except ImportError:
    import Queue as queue

# Uncomment to import from repo instead of site-packages.
#import os
#import sys
#parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.insert(0, parentdir)

from asyncthreads.reactor import Reactor
from asyncthreads.threadpool import ThreadPool

MIN_THREADS = 2
MAX_THREADS = 8

class TestReactor(object):

    @classmethod
    def setup_class(cls):
        gc.set_debug(gc.DEBUG_UNCOLLECTABLE)

        #cls.tp = None
        cls.tp = ThreadPool(MIN_THREADS, MAX_THREADS)
        cls.rktr = Reactor(cls.tp)
        cls.called = False
        cls.cb_event = threading.Event()
        cls.cb_rsp = None
        cls.defer_called = False

    def _func1(self):
        TestReactor.called = True
        return 'abc'

    def _func2(self, arg1, arg2):
        TestReactor.called = True
        return '-'.join([arg1, arg2])

    def _callback(self, rsp):
        TestReactor.cb_rsp = rsp
        TestReactor.cb_event.set()

    def _func_error(self):
        TestReactor.called = True
        raise Exception('some big problem')

    def _callback_error(self, rsp):
        raise Exception('problem in callback')

    def _defer_func2(self, arg1, arg2):
        TestReactor.defer_called = True
        d = self.rktr.defer_to_thread(self._func2, (arg1, arg2))
        return d

    def reset_called(self):
        TestReactor.called = False
        TestReactor.cb_event.clear()
        TestReactor.cb_rsp = None
        TestReactor.defer_called = False

    def test_start(self):
        print('Starting reactor')
        assert self.rktr is not None
        assert not self.rktr.is_alive()
        time.sleep(0)
        self.rktr.start()
        assert self.rktr.is_alive(), 'reactor should be alive'
        print('started')

    def test_call(self):
        """Run in main thread"""
        print('Calling function with no args in main thread')
        self.reset_called()
        result = self.rktr.call(self._func1)
        ret = result.result()
        assert self.called, 'called should be True'
        assert ret == 'abc', 'wrong result'

        print('Calling function in main thread')
        self.reset_called()
        result = self.rktr.call(self._func2, ('hello', 'world'))
        ret = result.result()
        assert self.called, 'called should be True'
        assert ret == 'hello-world'

        print('Calling function in main thread with callback')
        self.reset_called()
        result = self.rktr.call(self._func2, ('hello', 'world'),
                                self._callback)
        ret = result.result()
        assert self.called, 'called should be True'
        assert self.cb_event.wait(3), 'cb_event should be set'
        assert ret == 'hello-world'
        assert self.cb_rsp == 'hello-world'

    def test_call_args(self):
        """Test different arg representations"""
        print('Calling function with dict args')
        self.reset_called()
        result = self.rktr.call(self._func2, {'arg1':'hello', 'arg2':'world'})
        ret = result.result()
        assert self.called, 'called should be True'
        assert ret == 'hello-world'

    def test_call_in_thread(self):
        """Run in other thread"""
        print('Calling function in other thread')
        self.reset_called()
        result = self.rktr.call_in_thread(self._func2, ('hello', 'world'))
        ret = result.result()
        assert self.called, 'called should be True'
        assert ret == 'hello-world'

        print('Calling function in other thread with callback')
        self.reset_called()
        result = self.rktr.call_in_thread(self._func2, ('hello', 'world'),
                                          self._callback)
        ret = result.result()
        assert self.called, 'called should be True'
        assert self.cb_event.wait(3), 'cb_event should be set'
        assert ret == 'hello-world'
        assert self.cb_rsp == 'hello-world'

        if TestReactor.tp is not None:
            print('Threads in pool: %s' % TestReactor.tp.threads())
            assert TestReactor.tp.threads() > 0

    def test_call_scheduled(self):
        """Run scheduled in main thread"""
        print('Calling function in main thread in 3 seconds')
        self.reset_called()
        result = self.rktr.call_later(3, self._func2, ('hello', 'world'))

        assert not result.done(), 'should not have result yet'
        time.sleep(4)
        assert result.done(), 'should have result by now'

        ret = result.result()
        assert self.called, 'called should be True'
        assert ret == 'hello-world'

        print('Calling function in main thread with callback in 3 seconds')
        self.reset_called()
        result = self.rktr.call_later(3, self._func2, ('hello', 'world'),
                                      self._callback)

        assert not result.done(), 'should not have result yet'
        time.sleep(4)
        assert result.done(), 'should have result by now'

        ret = result.result()
        assert self.called, 'called should be True'
        assert self.cb_event.wait(3), 'cb_event should be set'
        assert ret == 'hello-world'
        assert self.cb_rsp == 'hello-world'

    def test_call_in_thread_scheduled(self):
        """Run in other thread"""
        print('Calling function in other thread in 3 seconds')
        self.reset_called()
        result = self.rktr.call_in_thread_later(3, self._func2,
                                                ('hello', 'world'))

        assert not result.done(), 'should not have result yet'
        time.sleep(4)
        assert result.done(), 'should have result by now'

        ret = result.result()
        assert self.called, 'called should be True'
        assert ret == 'hello-world'

        print('Calling function in other thread with callback in 3 seconds')
        self.reset_called()
        result = self.rktr.call_in_thread_later(
            3, self._func2, ('hello', 'world'), self._callback)

        assert not result.done(), 'should not have result yet'
        time.sleep(4)
        assert result.done(), 'should have result by now'

        ret = result.result()
        assert self.called, 'called should be True'
        assert self.cb_event.wait(3), 'cb_event should be set'
        assert ret == 'hello-world'
        assert self.cb_rsp == 'hello-world'

    def test_cancel_scheduled(self):
        """Cancel scheduled call"""
        self.reset_called()
        print('Calling function in 3 seconds')
        result = self.rktr.call_later(3, self._func2, ('hello', 'world'))
        assert not result.done(), 'should not have result yet'

        assert self.rktr.cancel_scheduled(result),\
               'failed to find scheduled task'
        time.sleep(4)
        rsp = result.result()
        assert result.canceled(), 'failed to mark result as canceled'

        assert rsp is None, 'result should be None'
        assert not self.called, 'called should be False'

    def test_exception_in_call(self):
        print('Calling function in main thread that raises exception')
        self.reset_called()
        result = self.rktr.call(self._func_error)
        # Check for expected excption
        ret = None
        with pytest.raises(Exception) as ex:
            ret = result.result()
        assert str(ex).endswith('some big problem')
        assert self.called, 'called should be True'
        assert ret is None, 'return should be None'
        assert len(result.traceback()) > 0, 'should be traceback info'

        print('Calling function in other thread that raises exception')
        self.reset_called()
        result = self.rktr.call_in_thread(self._func_error)

        # Check for expected excption
        ret = None
        with pytest.raises(Exception) as ex:
            ret = result.result()
        assert str(ex).endswith('some big problem')
        assert self.called, 'called should be True'
        assert ret is None, 'return should be None'
        assert len(result.traceback()) > 0, 'should be traceback info'

    def test_exception_in_callback(self):
        print('Calling function in main thread callback that raises exception')
        self.reset_called()
        result = self.rktr.call(self._func1, (), self._callback_error)
        with pytest.raises(Exception) as ex:
            result.result()
        assert len(result.traceback()) > 0, 'should be traceback info'
        assert str(ex).endswith('problem in callback')
        assert self.called, 'called should be True'

        print('Calling function in other thread callback that raises ',
              'exception')
        self.reset_called()
        result = self.rktr.call_in_thread(self._func1,(),self._callback_error)
        with pytest.raises(Exception) as ex:
            result.result()
        assert str(ex).endswith('problem in callback')
        assert self.called, 'called should be True'
        assert len(result.traceback()) > 0, 'should be traceback info'

    def test_defer_call(self):
        print('Calling func on reactor thread that defers processing to thread')
        self.reset_called()
        result = self.rktr.call(self._defer_func2, ('hello', 'world'))
        ret = result.result()
        assert self.called, 'called should be True'
        assert ret == 'hello-world'

    def test_result_queue(self):
        print('Calling 3 functions in pooled thread, with delay of 1, 2, and '\
              '3 seconds for each thread, and waiting for all results on '\
              'same result queue.')
        self.reset_called()
        rq = queue.Queue()
        # Enqueue out of order and make sure they are called in correct order.
        self.rktr.call_in_thread_later(3, self._func2, ('delay', 'three'),
                                       None, rq)
        self.rktr.call_in_thread_later(1, self._func2, ('delay', 'one'), None,
                                       rq)
        self.rktr.call_in_thread_later(2, self._func2, ('delay', 'two'), None,
                                       rq)
        count = 0
        while count < 3:
            r = rq.get(True, 5)
            count += 1
            ret = r.result()
            print('got result:', ret)
            if count == 1:
                assert ret == 'delay-one'
            elif count == 2:
                assert ret == 'delay-two'
            else:
                assert ret == 'delay-three'

    def test_map_in_thread(self):
        """Test map_call_in_thread() method."""
        def square(i):
            return i * i

        def mul(i, j):
            return i * j

        pairs = [(2,3), (3,4), (4,5), (5,6)]
        results = self.rktr.map_in_thread(mul, pairs)
        assert len(pairs) == len(results)
        for i, r in enumerate(results):
            x,y = pairs[i]
            print("%s * %s = %s" % (x,y,r))
            assert r == x * y

        results = self.rktr.map_in_thread(square, range(5))
        assert len(results) == 5
        for i, r in enumerate(results):
            print("%s * %s = %s" % (i,i,r))
            assert r == i * i

        future = self.rktr.map_in_thread_async(mul, pairs)
        results = future.result()
        assert len(pairs) == len(results)
        for i, r in enumerate(results):
            x,y = pairs[i]
            print("%s * %s = %s" % (x,y,r))
            assert r == x * y


    def test_shutdown(self):
        print('Shutting down reactor')
        self.rktr.shutdown()
        assert not self.rktr.is_alive(), 'reactor should not be alive'

    def test_memory_leaks(self):
        """Check for memory leaks"""
        # Test for any objects that cannot be freed.
        assert len(gc.garbage) == 0, 'uncollected garbage: '+str(gc.garbage)
