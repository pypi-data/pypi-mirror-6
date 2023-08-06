from behave.runner import Context, Runner

from ..command import Complete
from .command.scope_transition import Close, Open, Start, Stop

class ProcessContext(Context):

    """
    Extend Behave's stack handling to send commands to a consumer process.

    """

    @property
    def command_queue(self):
        return self.config.command_queue

    @property
    def return_queue(self):
        return self.config.return_queue

    def _push(self):
        self.command_queue.put(Open())
        completion = self.return_queue.get()
        assert isinstance(completion, Complete)

        return super()._push()

    def _pop(self):
        result = super()._pop()

        self.command_queue.put(Close())
        completion = self.return_queue.get()
        assert isinstance(completion, Complete)

        return result

class ProcessRunner(Runner):

    """
    Override Behave's internal Context handler with `ProcessContext`.

    """

    def run_hook(self, name, context, *args):
        if name == 'before_all':
            # Preserve context for calls to replicate the `after_all` hook call
            # from `run_with_paths`.
            self._original_context = self.context = ProcessContext(self)
            self.setup_capture()
            self.config.command_queue.put(Start())
            completion = self.config.return_queue.get()
            assert isinstance(completion, Complete)

            result = super().run_hook(name, self._original_context, *args)

        elif name == 'after_all':
            result = super().run_hook(name, self._original_context, *args)

            self.config.command_queue.put(Stop())
            completion = self.config.return_queue.get()
            assert isinstance(completion, Complete)

        else:
            result = super().run_hook(name, context, *args)

        return result
