"""
Usage of this library is triggered by using the initialize() function.

Simple fabfile.py:
>>> import fabpowertasks
>>> project_dir = os.path.dirname(__file__)
>>> fabpowertasks.initialize(globals(), project_dir)
"""
from fabpowertasks.config import Properties, SystemPaths
from fabpowertasks.vagrant import VagrantCommands
from fabpowertasks.deploy import DeployCommands
from fabpowertasks.testing import TestingCommands


def initialize(module_globals, project_dir,
               project_properties=None, project_tasks=None,
               project_inject_objs=None):
    """
    Initialises Fabric for a given project.
    """
    project_properties = (project_properties
                          or Properties.load_from_file('project.fabfile.json'))
    injection_objs = {
        'local_project_paths': SystemPaths(project_dir, project_properties),
        'vagrant_commands': VagrantCommands(),
        'deploy_commands': DeployCommands(),
        'testing_commands': TestingCommands()
    }
    project_inject_objs = project_inject_objs or {}
    injection_objs.update(project_inject_objs)

    project_tasks = project_tasks or []
    # extend project tasks with additional tasks defined by commands
    for obj in injection_objs.itervalues():
        if hasattr(obj, 'generate_tasks'):
            project_tasks.extend(obj.generate_tasks())

    for task in project_tasks:
        # simple dependency injection into generated tasks by key name
        for inject_name, obj in injection_objs.iteritems():
            if hasattr(task, inject_name):
                setattr(task, inject_name, obj)
        # add task to globals
        module_globals[task.name] = task
