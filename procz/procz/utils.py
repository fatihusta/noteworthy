import time

class TimedLoop():
    def __init__(self, limit_seconds):
        self.limit = limit_seconds

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def run_til(self, func, til = lambda x: x):
        while time.time() - self.start < self.limit:
            res = func()
            if til(res):
                return res
        raise Exception('Time is up!')
