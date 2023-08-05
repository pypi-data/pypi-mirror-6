"""
Reactor pattern to call queued functions in a separate thread.

Functions can be queued to be called by the reactor main thread, or by a thread
in the reactor's thread pool.  Functions can be be queued to be called
immediately (as soon as calling thread is available), or queued to be called at
a specified later time.

"""
__author__ = "Andrew Gillis"
__license__ = "http://www.opensource.org/licenses/mit-license.php"
__maintainer__ = "Andrew Gillis"
__email__ = "gillis.andrewj@gmail.com"

import threading
import traceback
import heapq
import time
try:
    import queue
except ImportError:
    import Queue as queue

from asyncthreads import completion
from asyncthreads import threadrunner


class Reactor(threading.Thread):

    """
    The Reactor executes queued functions in a single thread.  Functions can be
    executed immediately, in the order they are enqueued, or they can be
    executed at some later time.  Functions may also be executed, immediately
    or later, in threads separate from the reactor's main thread.

    All functions executed by the reactor have an associated Completion object.
    A Completion object allows the caller to wait for and retrieve the result
    of a function called by the reactor.

    The reason to use a Reactor is to execute functions in a separate thread,
    asynchronously, from the thread of the caller.

    """

    def __init__(self, thread_pool=None):
        """Initialize Reactor thread object and internal thread pool (if used).

        Arguments:
        thread_pool -- ThreadPool object to use to submit tasks to.  If this is
                       None, then the reactor will not use a thread pool and
                       will start threads directly.  Use a thread pool to
                       throttle concurrency and to avoid thread creation
                       overhead.

        """
        threading.Thread.__init__(self, None, None, None)
        self._call_queue = queue.Queue()
        self.idle_wake_sec = None
        if thread_pool is not None:
            self._thread_pool = thread_pool
        else:
            self._thread_pool = threadrunner.ThreadRunner()

        self._task_heap = []

    def call(self, func, args=None, callback=None, result_q=None):
        """Enqueue a function for the reactor to run in its main thread.

        The caller can wait on the response using the returned Completion
        object. Running a function in the reactor's main thread means that no
        other functions will be running in the reactor's main thread at the
        same time.  This can be used in place of other synchronization.

        Arguments:
        func     -- Function to execute.
        args     -- Argument tuple to pass to function.
        callback -- Optional callback that takes return from func as argument.
        result_q -- Optional response queue to place finished Completion on.

        Return:
        Completion object.

        """
        assert(self.is_alive()), 'reactor is not started'
        future = completion.Completion()
        self._call_queue.put(
            (completion._Task(future, func, args, callback, result_q),
             None, None))
        return future

    def call_later(self, delay, func, args=None, callback=None, result_q=None):
        """Run a function in the reactor's main thread at a later time.

        The caller can wait on the response using the returned Completion
        object.

        Arguments:
        delay    -- Seconds remaining until call give as int or float.
        func     -- Function to execute.
        args     -- Argument tuple to pass to function.
        callback -- Optional callback that takes return from func as argument.
        result_q -- Optional response queue to place complete Result on.

        Return:
        Completion object.

        """
        if delay:
            when = time.time() + delay
        else:
            when = 0

        return self.call_at(when, func, args, callback, result_q)

    def call_at(self, when, func, args=None, callback=None, result_q=None):
        """Run a function in the reactor's main thread at the specified time.

        Arguments:
        when     -- Absolute timestamp specifying when to call func, given as
                    int or float, using the same reference as time().
        func     -- Function to execute.
        args     -- Argument tuple to pass to function.
        callback -- Optional callback that takes return from func as argument.
        result_q -- Optional response queue to place complete Result on.

        Return:
        Completion object.

        """
        assert(self.is_alive()), 'reactor is not started'
        future = completion.Completion()
        self._call_queue.put(
            (completion._Task(future, func, args, callback, result_q),
            when, None))
        return future

    def call_in_thread(self, func, args=None, callback=None, result_q=None):
        """
        Run the given function in a separate thread.

        The caller can wait on the response using the returned Completion
        object.  A thread from the reactor's internal thread pool is used to
        avoid the overhead of creating a new thread.

        Arguments:
        func     -- Function to execute.
        args     -- Argument tuple to pass to function.
        callback -- Optional callback that takes return from func as argument.
        result_q -- Optional response queue to place finished Completion on.

        Return:
        Completion object.

        """
        assert(self.is_alive()), 'reactor is not started'
        return self._thread_pool.submit(func, args, callback, result_q)

    def call_in_thread_later(self, time_until_call, func, args=None,
                             callback=None, result_q=None):
        """Run the given function in a separate thread, at a later time.

        The caller can wait on the response using the returned Completion
        object.  A thread from the reactor's internal thread pool is used to
        avoid the overhead of creating a new thread.

        Arguments:
        time_until_call -- Seconds remaining until call.
        func            -- Function to execute.
        args            -- Argument tuple to pass to function.
        callback        -- Optional callback that takes return from func as
                           argument.
        result_q        -- Optional response queue to place Completion on.

        Return:
        Completion object.

        """
        assert(self.is_alive()), 'reactor is not started'
        if time_until_call:
            action_time = time.time() + time_until_call
        else:
            action_time = 0

        future = completion.Completion()
        self._call_queue.put(
            (completion._Task(future, func, args, callback, result_q),
             action_time, True))
        return future

    def map_in_thread(self, func, iterable, callback=None, chunksize=None):
        """Parallel equivalent to map() built-in function.

        Calls the map() method of the reactor's thread pool.  Blocks until all
        results are ready.

        See Executor.map() for description.

        Return:
        List of results from each call to func.

        """
        return self._thread_pool.map(func, iterable, callback)

    def map_in_thread_async(self, func, iterable, callback=None,
                            chunksize=None):
        """Variant of map_in_thread() which returns a Completion object.

        Calls the map_async() method of the reactor's thread pool.
        See Executor.map() for description.

        This method consumes an additional thread to collect the result from
        each call and return the array of results on a single Completion.

        Return:
        Completion object to wait on and retrieve result.  Completion result
        is a list of results from each call to func.

        """
        return self._thread_pool.map_async(func, iterable, callback, chunksize)

    def cancel_scheduled(self, future):
        """Cancel a call scheduled to be called at a later time.

        Arguments:
        future -- Completion object returned from call_later() or from
                  call_in_thread_later().

        Return:
        True if scheduled call was successfully canceled.  False if scheduled
        call was not found (already executed) or already canceled.

        """
        # The Completion's task_id cannot be checked in this method.  The
        # request must be placed on the reactor's call queue to ensure that a
        # scheduled task request is received by the reactor before this request
        # to cancel it is received.
        tmp_future = self.call(self._cancel_scheduled, future)
        # Wait for reactor to remove task, and return whether or not the task
        # was removed.
        return tmp_future.result()

    def shutdown(self, shutdown_threadpool=True):
        """Cause the reactor thread to exit gracefully.

        Arguments:
        shutdown_threadpool -- If True, and Reactor is using a ThreadPool, then
                               shutdown the ThreadPool.  Set this to false if
                               the ThreadPool instance is still in use outside
                               of this Reactor.

        Return:
        True if shutdown, False if Reactor not started.

        """
        if not self.is_alive():
            return False

        self._call_queue.put(None)
        # Wait for thread to exit.
        self.join()

        # Shutdown threadpool after reactor main thread has exited to ensure no
        # more tasks are submitted to the thread pool.
        if shutdown_threadpool:
            self._thread_pool.shutdown()

        return True

    def qsize(self):
        """Return number of items in the message queue."""
        return self._call_queue.qsize()

    def empty(self):
        """Return True is no items in the message queue."""
        return self._call_queue.empty()

    def defer_to_thread(self, func, args=None):
        """Defer execution from main thread to pooled thread.

        Allows execution to continue on a separate threads while using the
        caller's Completion object to return the result of the additional
        execution.  The original callback and result queue, if previously
        provided, are also used.

        Arguments:
        func     -- Function to execute in pooled thread.
        args     -- Arguments to pass to func.

        Returns:
        Special object recognized by Reactor to set up deferred call.

        """
        return completion._Task(None, func, args, self._deferred_thread)

    def defer(self, func, args=None):
        """Defer execution to process other tasks on main thread.

        Allows execution to continue as separate task while using the caller's
        original Completion object to return the result of the additional
        execution.  The original callback and result queue, if previously
        provided, are also used.

        Arguments:
        func     -- Function to execute in separate call on main thread.
        args     -- Arguments to pass to func.

        Returns:
        Special object recognized by Reactor to set up deferred call.

        """
        return completion._Task(None, func, args, self._deferred_call)

    #==========================================================================
    # Private methods follow:
    #==========================================================================

    def _deferred_thread(self, task):
        self._thread_pool.submit_task(task)

    def _deferred_call(self, task):
        self._call_queue.put((task, None, None))

    def _process_scheduled_queue(self):
        """Process all scheduled tasks that are currently due.

        """
        task_heap = self._task_heap
        # Execute the first task without checking the time, because this method
        # is only called when a scheduled task is due.
        task_time, task_id, task_data = heapq.heappop(task_heap)

        # If this task has been removed, then do nothing.
        if task_data is None:
            return

        def do_sched_task(task, _, in_thread):
            if in_thread:
                # Call thread pool to execute scheduled function.
                self._thread_pool.submit_task(task)
            else:
                #print('===> calling scheduled function')
                task.execute()

        do_sched_task(*task_data)
        if task_heap:
            now = time.time()
            next_time = task_heap[0][0]
            while task_heap and (not next_time or next_time <= now):
                task_time, task_id, task_data = heapq.heappop(task_heap)
                do_sched_task(*task_data)
                if task_heap:
                    next_time = task_heap[0][0]

    def _cancel_scheduled(self, future):
        """Mark a scheduled call, in scheduled task heap, as canceled.

        """
        task_id = future._task_id
        if task_id is None or task_id is False:
            # Task is not scheduled or is already canceled.
            return False
        task_heap = self._task_heap
        for idx, heap_item in enumerate(task_heap):
            task_time, heap_task_id, task_data = heap_item
            if heap_task_id == task_id:
                task, call_at, in_thread = task_data
                future = task.future
                future._rsp = None
                future._task_id = False
                future._call_done.set()
                # Need to keep task_id to preserve heap invariant.
                task_heap[idx] = (task_time, heap_task_id, None)
                return True
        return False

    def run(self):
        """Function run in thread, started by the start() method.

        """
        call_queue = self._call_queue
        task_heap = self._task_heap
        next_task_id = 0
        while True:
            sleep_time = None
            # If there are items on the scheduled task heap, then sleep until
            # next scheduled task is due.
            if task_heap:
                now = time.time()
                # Look at timer at top of heap.
                action_time = task_heap[0][0]
                if not action_time or action_time <= now:
                    sleep_time = 0
                else:
                    sleep_time = action_time - now

            try:
                #print('===> sleeping for %s seconds' % (sleep_time,))
                # Get the next function from the call queue.
                work_item = call_queue.get(True, sleep_time)
                if work_item is None:
                    break
                task, call_at, in_thread = work_item

                # If this is a new scheduled task.
                if call_at:
                    task.future._task_id = next_task_id
                    heapq.heappush(task_heap,
                                   (call_at, next_task_id, work_item))
                    next_task_id += 1
                else:
                    task.execute()

                del task

            except queue.Empty:
                # Woke up because it is time do next scheduled task.
                #print('===> woke up to do next scheduled task')
                self._process_scheduled_queue()
                continue

            except Exception:
                print('ERROR: '+str(traceback.format_exc()))

        return True

