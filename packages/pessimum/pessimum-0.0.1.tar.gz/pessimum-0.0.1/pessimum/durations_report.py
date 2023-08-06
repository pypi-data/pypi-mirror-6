from time import time


class DurationsReport(object):

    class Test(object):
        def __init__(self, test):
            self.reference = test
            self.start_time = time()
            self.end_time = None

        def end(self):
            self.end_time = time()

        @property
        def duration(self):
            return self.end_time - self.start_time

    def __init__(self):
        self.tests = []

    def start(self, test):
        self.tests.append(self.Test(test))

    def end(self, test):
        self.find_test(test).end()

    def find_test(self, the_test):
        for test in self.tests:
            if test.reference is the_test:
                return test

    def __iter__(self):
        return iter(self.tests)
