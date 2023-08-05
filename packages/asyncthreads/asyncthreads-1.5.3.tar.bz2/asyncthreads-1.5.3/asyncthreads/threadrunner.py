"""
Like ThreadPool, but submit() runs each task in a new thread.

"""
__author__ = "Andrew Gillis"
__license__ = "http://www.opensource.org/licenses/mit-license.php"
__maintainer__ = "Andrew Gillis"
__email__ = "gillis.andrewj@gmail.com"

import threading
from asyncthreads import executor


class ThreadRunner(executor.Executor):

    """
    Object similar to ThreadPool, but only launches new threads on submit().

    """
    def __init__(self):
        """Initialize the ThreadRunner instance.

        """
        executor.Executor.__init__(self)

    def submit_task(self, task):
        """Submit a task to execute in a new thread."""
        if self._shutdown:
            raise RuntimeError('cannot submit tasks after shutdown')
        th = threading.Thread(target=task.execute)
        th.daemon = True
        th.start()

    def shutdown(self, wait_for_threads=True, drop_queued_tasks=False):
        """See Executor.shutdown"""
        if self._shutdown:
            return False

        self._shutdown = True
        return True


