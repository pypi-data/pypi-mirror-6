from .base import DescribeModel, StepModel

class ScopeModel(DescribeModel):

    """
    Aggregate some typical constructor functionality for specific classes to
    grab by inheritence.

    """

    def __init__(self, model):
        self.name        = model.name
        self.description = model.description
        self.filename    = model.filename
        self.line        = model.line

    def __str__(self):
        return "%s\n  (%s:%s)" % (self.name, self.filename, self.line)

class Feature(ScopeModel):

    """
    Describe a feature to a consumer.

    """

    def __call__(self, return_queue, context):
        context.feature = self
        self.vacuous_return(return_queue)

    def __str__(self):
        return 'Feature: ' + super().__str__()

class Scenario(ScopeModel):

    """
    Describe a scenario to a consumer.

    """

    def __call__(self, return_queue, context):
        context.scenario = self
        self.vacuous_return(return_queue)

    def __str__(self):
        return 'Scenario: ' + super().__str__()

class Step(DescribeModel, StepModel):

    """
    Describe a step to a consumer.

    """

    def __call__(self, return_queue, context):
        context.step = self
        self.vacuous_return(return_queue)
