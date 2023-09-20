class BaseInit:
    """Base class that can be called by `hab_gui.utils.entry_point_init` to
    customize some part of hab_gui based on site configuration.

    You don't need to subclass this class, just make sure your class conforms to it.
    """

    def __init__(self, resolver, cmd, cli_args=None, **kwargs):
        super().__init__()
        self.resolver = resolver
        self.cmd = cmd
        self.cli_args = cli_args
        self.kwargs = kwargs
