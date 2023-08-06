from __future__ import absolute_import

try:
    import queue
except ImportError:
    import Queue as queue

import tg, uuid
from .progress import asyncjobs_progress_status

class AsyncJobQueue(object):
    def __init__(self):
        super(AsyncJobQueue, self).__init__()
        self.queue = queue.Queue()

    def get(self):
        return self.queue.get()

    def done(self, entryid):
        asyncjobs_progress_status.remove(entryid)
        self.queue.task_done()

    def perform(self, what, args, params):
        uid = 'asyncjob_%s' % str(uuid.uuid1())
        asyncjobs_progress_status.track(uid)
        self.queue.put({'callable':what,
                        'args':args,
                        'params':params,
                        'uid':uid})
        return uid

def asyncjob_perform(what, *args, **params):
    return tg.app_globals.asyncjob_queue.perform(what, args, params)
