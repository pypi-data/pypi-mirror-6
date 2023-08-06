class Complete(object):

    """
    Vacuous class whose type indicates a completed command.

    """

    pass

class Command(object):

    """
    Command protocol interface.

    Command instances must also be callable, but the number of arguments can
    vary with subprotocols. The first argument should always be a `Queue`
    instance intended for puting return values::

        def __call__(self, return_queue, ...):

    Any data attached to a command instance must be pickleable to allow
    interprocess transmission::
        def __init__(self, pickleable1, obj, ...):
            self.p1 = pickleable1
            self.p2 = obj.pickleable2
            ...

    A command is initiated with its `trigger` method. This method puts the
    command to a queue for consumption by another process. The method then
    blocks, waiting for a `Complete` instance on another queue. When a
    `Complete` instance arrives, `trigger` exits, allowing execution to
    continue.

    """

    def trigger(self, config):
        """
        Send command.
        """
        config.command_queue.put(self)
        completion = config.return_queue.get()
        assert isinstance(completion, Complete)

    @classmethod
    def vacuous_return(cls, return_queue):
        """
        Unblock `trigger` without doing anything.
        """
        return_queue.put(Complete())

class ScopeTransition(Command):

    """
    `ScopeTransition` protocol interface.

    `ScopeTransition` instances indicate that Behave has just moved from a scope
    level, e.g. feature-to-scenario and feature-to-global.

    """

    pass

class DescribeModel(Command):

    """
    `DescribeModel` protocol interface.

    `DescribeModel` instances get emitted when Behave has the current scope's
    data. See `Result` protocol for step results.

    """

    def __call__(self, return_queue, context):
        """
        Execute the command.

        :param return_queue: `Queue` to receive `Complete` instance upon
        completion of command handling.
        :param context: `Context` instance describing the Behave scope stack.
        """
        raise NotImplementedError

class InjectResource(Command):

    """
    `InjectResource` protocol interface.

    `InjectResource` instances instruct the command's consumer to ready a
    resource.

    """

    def __call__(self, return_queue, owner):
        """
        Execute the command.

        :param return_queue: `Queue` to receive `Complete` instance upon
        completion of command handling.
        :param owner: `BehaveSuite` instance managing the resource.
        """
        raise NotImplementedError

class StepModel(object):

    """
    Mixin object to provide shared constructor functionality.

    """

    def __init__(self, step):
        """
        Transfer pickleable attributes from Behave's step implementation to a
        blob class.

        :param step: `Step` instance from Behave.
        """
        self.name          = step.name
        self.text          = step.text
        self.type          = step.step_type
        self.filename      = step.filename
        self.line          = step.line
        self.status        = step.status
        self.error_message = step.error_message

    def __str__(self):
        return '%s: %s\n  (%s:%s)' % (
            self.type,
            self.name,
            self.filename,
            self.line)

class Result(Command):

    """
    `Result` protocol interface.

    `Result` instances describe a step result to a consumer.

    """

    def __init__(self, step, capture):
        """
        Extend `StepModel` with captured stream data from Behave.

        :param step: `Step` instance from Behave.
        :param capture: String data captured by Behave's stream capture
        mechanics.
        """
        super().__init__(step)
        self.capture = capture
