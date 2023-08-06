from time import time


class ProgressLogger(object):

    def __init__(self, iterable, output, timeout=5):
        self.output = output
        self.iterable = iterable

        if isinstance(iterable, (int, long, float)):
            self.length = iterable
        else:
            self.length = len(iterable)

        self.timeout = timeout
        self._timestamp = None
        self._counter = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __call__(self):
        self._counter += 1
        if not self.should_be_logged():
            return

        percent = int(self._counter * 100.0 / self.length)
        print >> self.output, '%s of %s (%s%%)' % (
            self._counter,
            self.length,
            percent)

    def __iter__(self):
        with self as step:
            for item in self.iterable:
                yield item
                step()

    def should_be_logged(self):
        now = float(time())

        if self._timestamp is None:
            self._timestamp = now
            return True

        next_stamp = self._timestamp + self.timeout
        if next_stamp <= now:
            self._timestamp = now
            return True

        else:
            return False
