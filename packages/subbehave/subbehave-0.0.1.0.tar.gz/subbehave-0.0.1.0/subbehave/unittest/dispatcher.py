from ..command import DescribeModel, InjectResource
from ..dispatcher import Dispatcher
from .command import ScopeTransition

def build_dispatcher(behave_config, suite, context):
    """
    Construct a `Dispatcher` instance to provide commands for unittest
    consumption.
    """
    command_queue = behave_config.command_queue
    return_queue = behave_config.return_queue
    d = Dispatcher(command_queue, return_queue)

    d.register(lambda c: isinstance(c, DescribeModel), context)
    d.register(lambda c: isinstance(c, InjectResource), suite)
    d.register(lambda c: isinstance(c, ScopeTransition), suite)

    return d
