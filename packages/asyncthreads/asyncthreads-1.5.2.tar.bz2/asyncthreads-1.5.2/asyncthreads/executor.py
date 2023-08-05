"""
Task execution interface.

Provides an interface that is implemented by ThreadPool classes.  A ThreadPool
used by the Reactor must support this interface.

"""
__author__ = "Andrew Gillis"
__license__ = "http://www.opensource.org/licenses/mit-license.php"
__maintainer__ = "Andrew Gillis"
__email__ = "gillis.andrewj@gmail.com"

from asyncthreads import completion


class Executor(object):

    """
    Abstract class that provides interface to execute function in separate
    thread and return result.

    """

    def __init__(self):
        """Initialize the thread pool and start the minimum number of threads.

        """
        self._shutdown = False

    def submit(self, function, args=None, callback=None, result_q=None):
        """Submit a function to be executed.

        Arguments:
        function -- Function to execute.
        args     -- Argument tuple to pass to function.
        callback -- Optional callback that takes return from func as argument.
        result_q -- Optional response queue to place Completion on.

        Return:
        Completion object to wait on and retrieve result of function.

        """
        future = completion.Completion()
        self.submit_task(
            completion._Task(future, function, args, callback, result_q))
        return future

    def map(self, func, iterable, callback=None):
        """Parallel equivalent to map() built-in function.

        Blocks until all results are ready.

        """
        futures = [self.submit(func, (i,), callback) for i in iterable]
        return [f.result() for f in futures]

    def map_async(self, func, iterable, callback=None):
        """Variant as map() which returns a Completion object immediately.

        This method consumes an extra thread to collect the result from each
        call and return the array of results on a single Completion.

        """
        return self.submit(self.map, (func, iterable, callback))

    def submit_task(self, task):
        """Submit a Task object for this executor to execute.

        Abstract method that must be implemented to execute Task.

        """
        return NotImplemented

    def shutdown(self, wait_for_threads, drop_queued_tasks):
        """Shutdown the Executor.

        Abstract method that must be implemented to shutdown Executor.

        Optionally wait for worker threads to exit and optionally drop any
        queued tasks, if these are applicable to this Executor.

        Arguments:
        wait_for_threads  -- Wait for all threads to complete, if applicable.
        drop_queued_tasks -- Discard remaining queued tasks, if applicable.

        Return:
        True if exited successfully, False if shutdown was already called.

        """
        return NotImplemented
