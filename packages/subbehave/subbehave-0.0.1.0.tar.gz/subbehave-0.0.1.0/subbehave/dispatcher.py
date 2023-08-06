import functools
import itertools

from .command.base import Result

class AmbiguousDispatcher(Exception):

    """
    Exception for `Dispatcher` instances to throw if there exists more than
    one matcher for a command.

    """

    def __init__(self, command):
        msg = 'More than one matcher found for command: %s'
        super().__init__(msg % command.__class__)

class UnhandledCommand(Exception):

    """
    Exception for `Dispatcher` instances to throw if a command falls through.

    """

    def __init__(self, command):
        msg = 'Cannot handle command: %s'
        super().__init__(msg % command.__class__)

class Dispatcher(object):

    """
    `Dispatcher` instances consume commands from a queue.

    """

    def __init__(self, command_queue, return_queue):
        self.__command_queue = command_queue
        self.__return_queue = return_queue
        self.__handlers = [[]]

    def register(self, matcher, arg):
        """
        Instruct the dispatcher to provide value `arg` to the commands that
        satisfy predicate `matcher`.

        :param matcher: Predicate function that takes a `Command` instance for
        its argument.
        :param arg: Value provided to `Command` instance if the `matcher`
        predicate is satisfied.
        """
        self.__handlers[-1].append((matcher,arg))

    def push(self):
        """
        Push a bin onto the registered instruction stack.

        After a call to `push`, calls to `register` will store new instructions
        independent of those registered earlier. A subsequent call to `pop` will
        remove these new instructions.
        """
        self.__handlers.append([])

    def pop(self):
        """
        Pop a bin from the registered instruction stack (see `push`).
        """
        self.__handlers.pop()

    def prime(self):
        """
        Consume commands until a `Result` instance is encountered.
        """
        peek = self.__command_queue.get()
        while not isinstance(peek, Result):
            hs = list(itertools.chain(*self.__handlers))
            hs.reverse() # Bias the choice toward top of stack.
            matches = list(filter(lambda pair: pair[0](peek), hs))
            if len(matches) == 1:
                arg = matches[0][1]
                peek(self.__return_queue, arg)
            elif len(matches) == 0:
                raise UnhandledCommand(peek)
            else:
                raise AmbiguousDispatcher(peek)
            peek = self.__command_queue.get()
        self.__command_queue.put(peek) # Leave the terminal in the queue.

    @property
    def next_command_caller(self):
        """
        Provide the command instance's `__call__` method with `return_queue`
        bound, leaving the remaining arguments to be provided elsewhere (see
        `command.base.Command`).
        """
        c = self.__command_queue.get()
        return functools.partial(c, self.__return_queue)
