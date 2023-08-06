from ...command import ScopeTransition as GenericScopeTransition

class ScopeTransition(GenericScopeTransition):

    """
    `ScopeTransition` protocol interface.

    `ScopeTransition` instances indicate that Behave has just moved from a scope
    level, e.g. feature-to-scenario and feature-to-global.

    """

    def __call__(self, return_queue, suite):
        """
        Execute the command.

        :param return_queue: `Queue` to receive `Complete` instance upon
        completion of command handling.
        :param suite: `BehaveSuite` instance.
        """
        raise NotImplementedError

class Open(ScopeTransition):

    """
    `Open` instances indicate that a Behave scope has been entered.

    """

    def __call__(self, return_queue, suite):
        """
        Push a new scope onto `suite`.
        """
        suite.pushScope()
        self.vacuous_return(return_queue)

class Start(Open):

    """
    `Start` instances indicate that a Behave has started.

    """

    pass

class Close(ScopeTransition):

    """
    `Close` instances indicate that a Behave scope has been exited.

    """

    def __call__(self, return_queue, suite):
        """
        Pop a scope from `suite`.
        """
        suite.popScope()
        self.vacuous_return(return_queue)

class Stop(Close):
    
    """
    `Stop` instances indicate that a Behave has stopped.

    """

    def __call__(self, return_queue, suite):
        """
        Extend `Close.__call__` to raise a `StopIteration` exception.
        """
        super().__call__(return_queue, suite)
        raise StopIteration
