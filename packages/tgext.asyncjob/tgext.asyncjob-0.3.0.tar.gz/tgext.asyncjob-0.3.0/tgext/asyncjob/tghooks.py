import logging
from tg import config
from .queue import AsyncJobQueue
from .worker import AsyncWorkerThread
from .progress import asyncjobs_progress_status

log = logging.getLogger('tgext.asyncjob')

def start_async_worker(app_globals=None, progress_tracker=None):
    if not app_globals:
        app_globals = config['tg.app_globals']

    if progress_tracker is None:
        from .trackers import memory
        progress_tracker = memory.MemoryProgressTracker()

    asyncjobs_progress_status._tracker = progress_tracker

    app_globals.asyncjob_queue = AsyncJobQueue()
    worker = AsyncWorkerThread(app_globals.asyncjob_queue)
    worker.daemon = True
    worker.start()
    return worker

