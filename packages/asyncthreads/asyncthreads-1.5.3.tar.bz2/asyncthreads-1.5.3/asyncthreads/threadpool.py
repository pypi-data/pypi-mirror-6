"""
Resizable thread pool.

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

from asyncthreads import executor


class ThreadPool(executor.Executor):

    """
    Resizable thread pool class.

    Maintain a pool of threads that execute tasks given to submit().  The
    number of worker threads can be changed by calling resize_pool() to set the
    number of workers explicitly, or by setting a max_size greater than
    min_size and letting to pool automatically change its size.

    """

    def __init__(self, min_size, max_size=0, queue_size=0):
        """Initialize the thread pool and start the minimum number of threads.

        If max_size is specified and is larger than min_size, then the pool
        will automatically resize.  If min_size is > 0 and max_size is zero,
        then max_size is set to min_size and thread pool is fixed at min_size.

        It is an error if min_size and max_size are both zero.

        Arguments:
        min_size    -- Minimum number of threads to have in pool.
        max_size    -- Optional.  Maximum size pool can grow to.
        queue_size  -- Maximum items allowed in task queue.   If queue_size is
                       less than or equal to zero, the queue size is infinite.

        """
        executor.Executor.__init__(self)
        self._set_size_limits(min_size, max_size)
        self._threads = 0
        self._task_queue = queue.Queue(queue_size)
        self._resize_lock = threading.Lock()
        self._idle_lock = threading.Lock()
        self._idle_count = 0

    def submit_task(self, task):
        """Insert a Task object into the queue.

        Useful for submitting task when Task object already exists.

        """
        with self._resize_lock:
            if self._shutdown:
                raise RuntimeError('cannot submit tasks after shutdown')

            self._task_queue.put(task, False)
            self._adjust_thread_count()

    def threads(self):
        """Return the number of threads in the pool."""
        return self._threads

    def idle_threads(self):
        """Return the current number of idle threads."""
        return self._idle_count

    def qsize(self):
        """Return the number of items currently in task queue."""
        return self._task_queue.qsize()

    def shutdown(self, wait_for_threads=True, drop_queued_tasks=False):
        """Shutdown the thread pool.

        Optionally wait for worker threads to exit, and optionally drop any
        queued tasks.

        Arguments:
        wait_for_threads  -- Wait for all threads to complete.
        drop_queued_tasks -- Discard any tasks that are on the task queue, but
                             have not yet been processed.  If not dropped,
                             tasks are processed before shutdown returns.

        Return:
        True if exited successfully, False if shutdown was already called.

        """
        with self._resize_lock:
            if self._shutdown:
                return False

            self._shutdown = True

            while drop_queued_tasks:
                # Discard remaining tasks on queue.
                try:
                    self._task_queue.get(False)
                    self._task_queue.task_done()
                except queue.Empty:
                    break

            # Enqueue a shutdown request for every thread.
            while self._threads:
                self._threads -= 1
                self._task_queue.put(None)

            # Wait until all shutdown requests are processed.
            if wait_for_threads:
                self._task_queue.join()

        return True

    def resize_pool(self, new_size, new_min=None, new_max=None):
        """Resize the thread pool to have the specified number of threads.

        If new pool size limits are not specified, then the number of threads
        in the pool will return to within the bounds originally specified.
        This is useful for temporarily sizing the pool outside the normal size
        limits.

        If new size limits are specified, then the pool automatically adjust to
        conform to the new bounds.

        Arguments:
        new_size -- New size (total number of threads) for pool to have.
        new_min  -- Optional new minimum size for pool.
        new_max  -- Optional new maximum size for pool.

        """
        if new_size < 0:
            raise ValueError('pool size must be >= 0')

        with self._resize_lock:
            if new_size > self._threads:
                # Growing pool.
                while self._threads < new_size:
                    self._threads += 1
                    t = threading.Thread(target=self._worker)
                    t.daemon = True
                    t.start()
            else:
                # Shrinking pool.
                while self._threads > new_size:
                    self._threads -= 1
                    self._task_queue.put(None)

            if new_min is not None or new_max is not None:
                if new_min is None:
                    new_min = self._min_size
                elif new_max is None:
                    new_max = self._max_size
                self._set_size_limits(new_min, new_max)

    def _adjust_thread_count(self):
        """If more items in the queue than idle threads, add thread.

        """
        idle = self._idle_count
        qsize = self._task_queue.qsize()

        # Grow pool if there are more items in queue than there idle threads.
        if qsize > idle:
            if self._threads < self._max_size:
                t = threading.Thread(target=self._worker)
                t.daemon = True
                t.start()
                self._threads += 1

        # Shrink pool if fewer items in queue than idle threads above minimum
        # size, and more idle threads than the minimum pool size.
        elif idle > self._min_size and qsize < idle:
            self._task_queue.put(None)
            self._threads -= 1

    def _set_size_limits(self, min_size, max_size):
        assert(isinstance(min_size, int)), 'min_size must be int'
        assert(isinstance(max_size, int)), 'max_size must be int'

        # Validate and set min_size
        if min_size <= 0 and max_size <= 0:
            raise ValueError('min_size and/or max_size must be > 0')
        if min_size < 0:
            min_size = 0
        self._min_size = min_size

        if max_size <= 0:
            # Pool is manually resizeable only.
            max_size = min_size
        elif max_size < min_size:
            raise ValueError('max_size must be 0 or >= min_size')
        # Pool is automatically resizeable if max_size > min_size.
        self._max_size = max_size

    def _worker(self):
        """Retrieve the next task and execute it, calling the callback if any.

        """
        task_queue = self._task_queue
        idle_lock = self._idle_lock
        while True:
            try:
                task = task_queue.get(False)
            except queue.Empty:
                with idle_lock:
                    self._idle_count += 1
                # Wait forever.
                task = task_queue.get()
                with idle_lock:
                    self._idle_count -= 1

            # Exit if told to quit.
            if task is None:
                task_queue.task_done()
                break

            # Execute task.
            task.execute()

            del task
            task_queue.task_done()
