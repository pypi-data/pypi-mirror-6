from behave.formatter.pretty import PrettyFormatter

from .command.describe_model import Feature, Scenario, Step

class BlockingFormatter(PrettyFormatter):

    """
    A Behave formatter that converts Behave events into commands for consumption
    by another process.

    Another class must derive from `BlockingFormatter` and provide it a
    `results` map. See `unittest.suite.UnittestFormatter` for a typical use
    case.

    """

    name = 'blocking.pretty'
    description = 'Formatter that fails miserably (replace the results value with a map to backend results).'
    results = {
        'passed'    : None,
        'skipped'   : None,
        'failed'    : None,
        'undefined' : None,
        'untested'  : None}

    def feature(self, feature):
        """
        Extend `feature` to trigger a command.
        """
        super().feature(feature)
        Feature(feature).trigger(self.config)

    def scenario(self, scenario):
        """
        Extend `scenario` to trigger a command.
        """
        super().scenario(scenario)
        Scenario(scenario).trigger(self.config)

    def step(self, step):
        """
        Extend `step` to trigger a command.
        """
        super().step(step)
        Step(step).trigger(self.config)

    def result(self, step_result):
        """
        Extend `result` to trigger a command.
        """
        self.stream.truncate(0)
        super().result(step_result)
        capture = self.stream.getvalue().decode()

        Result = self.results.get(step_result.status, None)
        if Result:
            Result(step_result, capture).trigger(self.config)
        else:
            msg = 'Unhandled result status: %s'
            raise NotImplementedError(msg % step_result.status)
