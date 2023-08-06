from unittest.runner import TextTestResult

class PyunitResult(TextTestResult):

    """
    Override the default result type from `unittest` to avoid accessing
    exceptions.

    An exception's traceback cannot be pickled, so we can't use the `unittest`
    norm.

    """

    def addError(self, test, err):
        self.errors.append((test, err))
        if self.showAll:
            self.stream.writeln("ERROR")
        elif self.dots:
            self.stream.write('E')
            self.stream.flush()

    def addFailure(self, test, err):
        self.failures.append((test, err))
        if self.showAll:
            self.stream.writeln("FAIL")
        elif self.dots:
            self.stream.write('F')
            self.stream.flush()

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.showAll:
            self.stream.writeln("skipped {0!r}".format(reason))
        elif self.dots:
            self.stream.write("s")
            self.stream.flush()

    def addExpectedFailure(self, test, err):
        raise NotImplementedError

    def addUnexpectedSuccess(self, test):
        raise NotImplementedError
