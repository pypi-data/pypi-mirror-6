class Context(object):

    """
    Caches feature, scenario, and steps from a Behave scan.

    Automatically clobber subscopes when outer scopes get set.

    """

    def __init__(self):
        self.feature = None

    @property
    def feature(self):
        return self.__feature
    @feature.setter
    def feature(self, value):
        self.__feature = value
        self.scenario = None

    @property
    def scenario(self):
        return self.__scenario
    @scenario.setter
    def scenario(self, value):
        self.__scenario = value
        self.step = None

    def __str__(self):
        return '%s\n%s\n%s' % (self.feature, self.scenario, self.step)
