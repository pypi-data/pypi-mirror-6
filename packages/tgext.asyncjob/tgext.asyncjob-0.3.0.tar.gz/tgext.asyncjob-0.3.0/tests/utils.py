import time

class TestTask(object):
    def __init__(self):
        self.force_completion = False
        self.ended = False
        self.started = False
        self.perform_calls = []

    def __call__(self, *args, **kw):
        self.started = True

        try:
            while not self.force_completion:
                if self.perform_calls:
                    method, args = self.perform_calls.pop()
                    method(*args)
                time.sleep(0.01)
        finally:
            self.ended = True

    def _wait_for_end(self):
        while not self.ended:
            time.sleep(0.01)

    def wait_for_start(self):
        while not self.started:
            time.sleep(0.01)

    def complete(self):
        self.force_completion = True
        self._wait_for_end()

    def call_from_thread(self, method, *args):
        self.perform_calls.append((method, args))
        self._wait_for_calls_completion()

    def _wait_for_calls_completion(self):
        while self.perform_calls:
            time.sleep(0.01)