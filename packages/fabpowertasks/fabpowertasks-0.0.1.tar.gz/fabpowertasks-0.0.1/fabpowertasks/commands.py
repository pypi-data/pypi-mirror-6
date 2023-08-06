"""
The base commands functionality for all Fabric tasks
"""
from fabric.tasks import Task


class BaseCommands(object):
    """
    Offers simple interface to generate Fabric tasks from object functions
    """

    def __init__(self):
        self._task_functions = []

    @property
    def task_functions(self):
        return self._task_functions

    def generate_tasks(self):
        """
        Generates the tasks from the commands interface
        """
        tasks = []
        for function in self.task_functions:
            # construct task wrapper class from function given
            wrapper = self._make_task_wrapper(function)
            wrapper.__doc__ = function.__doc__
            wrapper.name = function.__name__
            # decorate class with empty attrs for DI
            inject_attrs = self.get_inject_attributes()
            for attr in inject_attrs:
                setattr(wrapper, attr, None)
            tasks.append(wrapper)
        return tasks

    def get_inject_attributes(self):
        """
        Return the list of attributes that can be used as injection for command
        tasks.
        Defaults to all public instance attributes that are set to None.
        """
        return map(
            lambda item: item[0],
            filter(lambda item: not item[0].startswith('_') and item[1] is None,
                   vars(self).items())
        )

    def _make_task_wrapper(self, function):
        class TaskWrapper(Task):
            def __init__(self, klass):
                super(TaskWrapper, self).__init__()
                self.klass = klass

            def __setattr__(self, key, value):
                """
                Setting the underlying attributes of the
                wrapped command class.
                """
                super(TaskWrapper, self).__setattr__(key, value)
                if hasattr(self, 'klass'):
                    setattr(self.klass, key, value)

            def run(self, *args, **kwargs):
                function(*args, **kwargs)
        return TaskWrapper(self)
