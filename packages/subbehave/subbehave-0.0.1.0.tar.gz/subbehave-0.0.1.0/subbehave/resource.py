class Resource(object):
    """
    `Resource` protocol interface.

    Resource implementors expose some resource for Behave to by emitting
    commands.

    """

    command_type = None

    def create(self):
        """
        Set up the resource.
        """
        raise NotImplementedError

    def register(self, dispatcher):
        """
        Register the resource with a dispatcher. See
        `subbehave.dispatcher.Dispatcher`.
        """
        dispatcher.register(lambda c: isinstance(c, self.command_type), self)

    def destroy(self):
        """
        Tear down the resource.
        """
        raise NotImplementedError
