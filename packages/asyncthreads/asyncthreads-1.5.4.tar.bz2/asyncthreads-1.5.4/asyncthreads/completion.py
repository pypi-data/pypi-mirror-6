"""
Wait for an get results of asynchronous function call.

"""
__author__ = "Andrew Gillis"
__license__ = "http://www.opensource.org/licenses/mit-license.php"
__maintainer__ = "Andrew Gillis"
__email__ = "gillis.andrewj@gmail.com"

import threading
try:
    import queue
except ImportError:
    import Queue as queue
from collections import Callable
import traceback


class Completion(object):

    """
    Completion represents the result of an asynchronous computation.

    A Completion object is returned by a Reactor's call_() methods.  It holds a
    value that may become available at some point.  The Completion class is
    equivalent to the Future class offered by other concurrency frameworks.

    The Completion object allows the caller to wait for and retrieve the result
    of a function called by the Reactor.  This not only includes any return
    from the called function, but any exception as well.

    A Completion object is also used to identify a scheduled function to
    cancel, and it can be used to check if a scheduled call has been canceled.

    """

    slots = ('_call_done', '_rsp', '_exception', '_traceback_str', '_task_id')
    def __init__(self):
        self._call_done = threading.Event()
        self._rsp = None
        self._exception = None
        self._traceback_str = None

        # For canceling scheduled tasks.  This is kept here to allow task to be
        # retrieved using Completion object.
        self._task_id = None

    def result(self, timeout=None):
        """Return the value returned by the call.

        If the call has not yet completed then wait up to timeout seconds or
        until call complete if timeout is None.  It timeout occurs, then raise
        a RuntimeError exception.  If canceled before completion, then a
        ThreadError exception is raised.

        If the call raised an exception, then this methods returns the same
        exception.

        """
        if self._call_done.wait(timeout):
            if self._exception:
                raise self._exception

            return self._rsp

        if self.canceled():
            # Canceled before completed.
            raise threading.ThreadError('call canceled before completion')

        # Timeout waiting for completion.
        raise RuntimeError('timeout waiting for result')

    def wait(self, timeout=None):
        """Wait until the result is available or until timeout seconds pass."""
        return self._call_done.wait(timeout)

    def done(self):
        """Return True if call completed or canceled."""
        return self._call_done.is_set()

    def traceback(self):
        """Return the traceback string from exception in call."""
        return self._traceback_str

    def canceled(self):
        return self._task_id is False

    def successful(self):
        """Return whether the call completed without raising an exception.

        Raises AssertionError if the result is not ready.

        """
        if not self._call_done.is_set():
            raise AssertionError('call not completed')
        return not self._exception


class _Task(object):

    """
    Internal container for task execution data.

    Task objects hold information needed for an executor (ThreadPool, Reactor)
    to execute a user-specified function, return a result, and notify the
    caller about the completion of the function call.

    """

    slots = ('future', 'func', 'args', 'callback', 'result_q')
    def __init__(self, future, func, args=None, callback=None, result_q=None):
        """Initialize Task object.

        Arguments:
        future   -- Completion object used to return result and notify caller
                    that function call has completed.
        func     -- Function to execute.
        args     -- Argument tuple to pass to function.
        callback -- Optional callback that takes return from func as argument.
                    Function call is not completed until after callback
                    function has returned.
        result_q -- Optional response queue to place Completion on.

        """
        assert(future is None or
               isinstance(future, Completion)), 'first arg must be Completion'
        assert(isinstance(func, Callable)), 'function is not callable'
        assert(callback is None or
               isinstance(callback, Callable)),'callback is not callable'
        assert(result_q is None or
               isinstance(result_q, queue.Queue)), 'result_q is not Queue'

        self.future = future
        self.func = func
        self.args = args
        self.callback = callback
        self.result_q = result_q

    def execute(self):
        """Execute task function and handle result.

        This method is executed by the executor to which this Task object was
        submitted.

        """
        # Execute task.
        args = self.args
        future = self.future
        func = self.func
        try:
            if args is None:
                ret = func()
            elif isinstance(args, (tuple, list, set)):
                ret = func(*args)
            elif isinstance(args, dict):
                ret = func(**args)
            else:
                ret = func(args)

            if isinstance(ret, _Task):
                defer_func = ret.callback # ret.callback holds defer function.
                ret.future = future # use original Completion
                ret.callback = self.callback # use original callback
                ret.result_q = self.result_q # use original result queue
                defer_func(ret)
                return

            if self.callback is not None:
                self.callback(ret)
        except Exception as e:
            ret = None
            future._exception = e
            future._traceback_str = traceback.format_exc()

        # Set call done only after callback has completed.  This is necessary
        # for code waiting on a Completion to be able to reliably see an
        # exception from a callback.
        future._rsp = ret
        future._call_done.set()

        if self.result_q:
            # If a result queue specified, then put finished Completion object
            # onto result queue.
            try:
                self.result_q.put(future)
            except queue.Full:
                pass
