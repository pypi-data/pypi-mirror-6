from fabric.api import local, shell_env
from fabpowertasks.commands import BaseCommands


class TestingCommands(BaseCommands):
    """
    Common tasks to run when working with a Vagrant deployment scheme.
    """

    def __init__(self):
        super(TestingCommands, self).__init__()
        self.local_project_paths = None
        self._task_functions = [self.pytest]

    def pytest(self, *paths):
        """
        Runs the given test paths with py.test
        """
        with shell_env(PYTHONPATH=self.local_project_paths.base_dir):
            local('py.test %s' % ' '.join(paths))
