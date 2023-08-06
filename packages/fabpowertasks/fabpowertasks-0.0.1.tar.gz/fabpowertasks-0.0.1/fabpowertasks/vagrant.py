"""
Vagrant-specific commands
"""
from fabric import api

from fabpowertasks.commands import BaseCommands
from fabpowertasks.util import convert_to_cmd_options


class VagrantCommands(BaseCommands):
    """
    Common tasks to run when working with a Vagrant deployment scheme.
    """

    def __init__(self):
        super(VagrantCommands, self).__init__()
        self.local_project_paths = None
        self._task_functions = [self.vagrant]

    def vagrant(self, *args, **kwargs):
        """
        Run arbitrary vagrant commands e.g. vagrant up, vagrant halt, etc.
        """
        if len(args) == 0:
            api.abort('Missing required Vagrant command')
        cmd_options = convert_to_cmd_options(args, kwargs)
        with api.lcd(self.local_project_paths.deployment_dir):
            api.local('vagrant %s' % cmd_options)
