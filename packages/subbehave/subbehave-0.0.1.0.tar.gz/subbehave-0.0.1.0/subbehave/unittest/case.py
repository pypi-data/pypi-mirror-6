from unittest.case import TestCase

class StepTestCase(TestCase):

    """
    Call a provided command to log test results.

    """

    def __init__(self, context, command_caller):
        self.context = context
        self._command_caller = command_caller

    def __str__(self):
        return str(self.context)

    def shortDescription(self):
        if self.context.step.text:
            return self.context.step.text.split("\n")[0].strip() or None
        else:
            return None

    def run(self, result):
        result.startTest(self)
        self._command_caller(self, result)
        result.stopTest(self)

        return result
