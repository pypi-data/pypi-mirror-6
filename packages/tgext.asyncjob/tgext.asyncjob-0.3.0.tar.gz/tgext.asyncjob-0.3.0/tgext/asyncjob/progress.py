from .worker import asyncjob_running_uid

class ProgressTrackerProxy(object):
    def __init__(self):
        self._tracker = None

    def __getattr__(self, item):
        return getattr(self._tracker, item)

#This should actually be refactored to remove global instance
asyncjobs_progress_status = ProgressTrackerProxy()

def asyncjob_set_progress(value, data=None):
    entryid = asyncjob_running_uid()
    asyncjobs_progress_status.set_progress(entryid, value, data)

def asyncjob_get_progress(entryid):
    return asyncjobs_progress_status.get_progress(entryid)
