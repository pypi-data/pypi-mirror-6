"""
Common configuration for all Fabric tasks
"""
from fabric import api
import os
import json


class SystemPaths(object):
    """
    Defines a simple interface to retrieve path information for a project
    """

    def __init__(self, base_dir, properties, os_type=None):
        """
        Initialises the system path object with the given base directory and
        project properties. May optionally specify the OS type used for all
        path creation and checks.

        :param base_dir:
        :param properties:
        :param os_type: defaults to local OS type
        """
        super(SystemPaths, self).__init__()
        self.base_dir = base_dir
        self.properties = properties
        self._path = None
        if os_type is None:
            os_type = os.uname()[0].lower()
        self.os_type = os_type

    @property
    def path(self):
        """
        Returns the path module for this system.
        """
        if self._path is None:
            if self.os_type == 'linux' or self.os_type == 'darwin':
                import posixpath
                self._path = posixpath
            elif self.os_type == 'win32':
                import ntpath
                self._path = ntpath
            else:
                api.abort('Invalid OS type %s' % self._path)
        return self._path

    @property
    def deployment_dir(self):
        """
        Directory for deployment configuration of the project
        """
        return self.get_absolute_path(*self.properties.deployment_dir)

    @property
    def remote_deploy_dirs(self):
        """
        List of absolute directory paths that should be deployed remotely for
        this project.
        """
        return map(lambda dirs: self.get_absolute_path(*dirs),
                   self.properties.remote_deploy_dirs)

    def get_absolute_path(self, *components):
        """
        Returns the absolute path to the given list of path components

        :param components:
        """
        path = self.path.join(*components)
        if not self.path.isabs(path):
            path = self.path.join(self.base_dir, path)
        return path


class Properties(object):
    """
    Defines a collection of project properties used for injecting into
    commands and custom tasks.
    """

    # dir containing all deployment configuration, such as Vagrantfile, nginx
    # confs, etc.
    deployment_dir = ['deployment']
    # when deploying project remotely, defines list of directories to deploy -
    # mirrors both local and remote paths
    remote_deploy_dirs = [
        ['.']
    ]

    @classmethod
    def load_from_file(cls, path):
        """
        Instantiates an instance from the given JSON path

        :param path:
        """
        data = {}
        if os.path.exists(path):
            with open(path, 'rb') as handle:
                data = json.load(handle)

        instance = Properties()
        for key, value in data.iteritems():
            setattr(instance, key, value)

        return instance
