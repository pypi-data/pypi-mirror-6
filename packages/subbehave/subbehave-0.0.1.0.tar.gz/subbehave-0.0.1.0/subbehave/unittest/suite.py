from io import BytesIO
from multiprocessing import Process, Queue
from unittest.suite import BaseTestSuite

from behave.configuration import Configuration
from behave.formatter.base import StreamOpener
from behave.formatter.formatters import register

from ..context import Context
from ..formatter import BlockingFormatter
from .case import StepTestCase
from .command import behave_results
from .dispatcher import build_dispatcher
from .runner import ProcessRunner

class UnittestFormatter(BlockingFormatter):

    """
    Provide a `results` map to the `BlockingFormatter` superclass.

    """

    description = 'Formatter that provides provides commands to a BehaveSuite instance.'
    results = behave_results.copy()

register(UnittestFormatter)

class StepStream(object):

    """
    Wraps a dispatcher instance to provide an iterator interface to instances
    of `subbehave.command.Result`. The dispatcher can't handle the results, but
    it can prime them for consumption with the `return_queue` argument (see
    `subbehave.dispatcher.Dispatcher` and `subbehave.command.Command`).

    """

    def __init__(self, context, dispatcher):
        self.context = context
        self._dispatcher = dispatcher

    def __next__(self):
        self._dispatcher.prime()
        return StepTestCase(self.context, self._dispatcher.next_command_caller)

class BehaveSuite(BaseTestSuite):

    """
    Unittest test suite that consumes behave commands.

    """

    def __init__(self, features_directories):
        if isinstance(features_directories, str):
            features_directories = [features_directories]

        # Set up the Behave process.
        config = BehaveSuite.configuration(features_directories)
        #parametrize capture (in static config fn?)
        runner = ProcessRunner(config)
        self.behave_process = Process(target=runner.run)

        # Set up the Behave process's consumer.
        self._resources = []
        self._context = Context()

        self._dispatcher = build_dispatcher(config, self, self._context)

    def __repr__(self):
        return '<BehaveSuite>'

    def pushScope(self):
        """
        Push a bin onto the resources stack.

        After a call to `pushScope`, calls to `attachResource` will store new
        resources independent of those attached earlier.  A subsequent call to
        `popScope` will remove and destroy these new resources.
        """
        self._resources.append([])
        self._dispatcher.push()

    def popScope(self):
        """
        Pop a bin from the resources stack, calling the `destroy` method for
        each resource (see `pushScope`).
        """
        self._dispatcher.pop()
        for r in self._resources.pop():
            r.destroy()

    def attachResource(self, resource):
        """
        Attach a resource to the suite.

        Attached resources are available to all scopes until the current bin is
        popped. This method calls the resource's `Resource.create` method, so
        the caller need not. See `pushScope` and `popScope`.

        :param resource: `Resource` instance to add to the current bin.
        """
        resource.create()
        resource.register(self._dispatcher)
        self._resources[-1].append(resource)

    def __iter__(self):
        return StepStream(self._context, self._dispatcher)

    def run(self, result):
        """
        Extend the `unittest.suite.BaseTestSuite.run` to begin the Behave feeder
        process before running the suite itself.
        """
        self.behave_process.start()
        result = super().run(result)
        self.behave_process.join()

        return result

    @staticmethod
    def configuration(features_directories):
        """
        Build the Behave feeder process's configuration.
        """
        config = Configuration()
        config.command_queue = Queue()
        config.return_queue = Queue()
        config.show_snippets = False
        config.summary = False
        config.format = ['blocking.pretty']
        config.outputs = [StreamOpener(stream=BytesIO())] # Clobber stdout
        config.reporters = []
        config.paths = features_directories

        return config
