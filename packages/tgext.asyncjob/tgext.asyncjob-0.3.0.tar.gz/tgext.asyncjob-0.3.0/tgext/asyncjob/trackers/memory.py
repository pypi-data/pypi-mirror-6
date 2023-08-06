import threading

class MemoryProgressTracker(object):
    def __init__(self):
        super(MemoryProgressTracker, self).__init__()
        self.status_lock = threading.Lock()
        self.status = {}

    def track(self, entryid):
        with self.status_lock:
            self.status[entryid] = (-1, None)

    def remove(self, entryid):
        with self.status_lock:
            self.status.pop(entryid, None)

    def set_progress(self, entryid, value, message):
        with self.status_lock:
            self.status[entryid] = (value, message)

    def get_progress(self, entryid):
        with self.status_lock:
            return self.status.get(entryid)