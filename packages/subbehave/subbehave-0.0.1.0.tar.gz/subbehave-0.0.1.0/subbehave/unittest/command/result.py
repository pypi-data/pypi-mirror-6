from ...command.base import StepModel
from ...command.base import Result as GenericResult

class Result(GenericResult, StepModel):

    """
    `Result` protocol interface.

    `Result` instances describe a step result to a `unittest` consumer.

    """

    def __call__(self, return_queue, test, pyunit_result):
        """
        Execute the command.

        :param return_queue: `Queue` to receive `Complete` instance upon
        completion of command handling.
        :param test: `StepTestCase` instance
        :param pyunit_result: `Result` instance from `unittest`
        """
        raise NotImplementedError

class Succeed(Result, StepModel):

    """
    `Succeed` instances indicate that a Behave step has executed successfully.

    """

    def __call__(self, return_queue, test, pyunit_result):
        pyunit_result.addSuccess(test)
        self.vacuous_return(return_queue)

class Skip(Result, StepModel):

    """
    `Skip` instances indicate that a Behave step has been skipped.

    """

    def __call__(self, return_queue, test, pyunit_result):
        """
        Execute the command.

        TODO: The `addSkip` method from `unittest` requires a reason argument.
        The used message is a little tautological, but will suffice for now.
        """
        msg = 'Skipped Step: %s %s.'
        pyunit_result.addSkip(test, msg % (self.type.upper(), self.name))
        self.vacuous_return(return_queue)

class Untested(Skip):

    """
    `Untested` instances indicate that a Behave step has been ignored.

    """

    def __call__(self, return_queue, test, pyunit_result):
        """
        Execute the command.

        TODO: The `addSkip` method from `unittest` requires a reason argument.
        The used message is a little tautological, but will suffice for now.
        """
        msg = 'Untested Step: %s %s.'
        pyunit_result.addSkip(test, msg % (self.type.upper(), self.name))
        self.vacuous_return(return_queue)

class Fail(Result, StepModel):

    """
    `Fail` instances indicate that a Behave step has failed.

    TODO: Behave lumps errors and failures together. If I recall, a replacement
    `behave.model.Step` implementation would be needed to separate the two. Then
    an Error command parallel to this one will be needed.

    """

    def __call__(self, return_queue, test, pyunit_result):
        msg = self.error_message.strip()
        pyunit_result.addFailure(test, msg)
        self.vacuous_return(return_queue)

class Undefined(Fail):

    """
    `Undefined` instances indicate that a Behave step was prescribed but not
    implemented.

    """

    def __call__(self, return_queue, test, pyunit_result):
        msg = 'Undefined Step: %s %s'
        pyunit_result.addFailure(test, msg % (self.type.upper(), self.name))
        self.vacuous_return(return_queue)

# map for parametrization of a Formatter instance
behave_results = {
    'passed'    : Succeed,
    'skipped'   : Skip,
    'failed'    : Fail,
    'undefined' : Undefined,
    'untested'  : Untested}
