from fabtools.vagrant import vagrant_settings
from fabric.contrib.project import rsync_project
from fabric import api
from fabpowertasks.commands import BaseCommands


class DeployCommands(BaseCommands):
    """
    Standard tasks for deploying your project
    """

    def __init__(self):
        super(DeployCommands, self).__init__()
        self._task_functions = [self.vagrant_deploy]
        self.local_project_paths = None
        self.remote_project_paths = None

    def vagrant_deploy(self, box_name=''):
        """
        Deploys the project to the named vagrant box, or the default vagrant
        box if no name is given.

        :param box_name: name of the vagrant box to which to deploy
        """
        with vagrant_settings(box_name):
            api.run('mkdir %s' % self.remote_project_paths.base_dir)
            local_deploy_dirs = self.local_project_paths.remote_deploy_dirs
            remote_deploy_dirs = self.remote_project_paths.remote_deploy_dirs
            for index, local_deploy_dir in enumerate(local_deploy_dirs):
                rsync_project(remote_deploy_dirs[index],
                              local_dir=local_deploy_dir)
