## fabpowertasks

Offers an alternative to the standard way of generating Fabric tasks. Instead
of random functions or Task declarations, instead create Commands classes that
use a simple configuration flow and allow for dependency injection to share
functionality between Tasks.

Additionally, some simple tasks are auto-generated and act as examples of how
to write Commands.

### Examples

Here's a simple fabfile.py:

    import fabpowertasks
    project_dir = os.path.dirname(__file__)
    fabpowertasks.initialize(globals(), project_dir)

This automatically generates the Fabric tasks that come with fabpowertasks. They
can be run as standard using Fabric with ```fab <command>```

But that's not all - here's a more complex example ```fabfile/__init__.py```
that includes custom tasks:

    import os
    import fabpowertasks
    from fabfile.config import ProjectPaths
    from fabfile.tasks import CustomCommands

    fabfile_dir = os.path.dirname(__file__)
    project_dir = os.path.dirname(fabfile_dir)
    properties = fabpowertasks.Properties.load_from_file(
        os.path.join(fabfile_dir, 'project.json')
    )
    properties.base_dir = project_dir
    local_project_paths = ProjectPaths(project_dir, properties)
    injection_objs = {
        'local_project_paths': local_project_paths,
        'remote_project_paths': fabpowertasks.SystemPaths(properties.remote_base_dir,
                                                          properties),
        'custom_commands': CustomCommands()
    }
    fabpowertasks.initialize(globals(), os.path.dirname(fabfile_dir),
                             project_properties=properties,
                             project_inject_objs=injection_objs)

Some explanation of this example is needed:

* ```CustomCommands``` is a class that extends the utility class
```fabpowertasks.commands.BaseCommands```. This class comes with some additional
functions that are used to generate Fabric tasks from itself.
* An instance of the ```Properties``` class is used extensively throughout the
library and contains all project properties. At the very least, it requires
a project directory location, which is why this is a required option to
```initialize()```. But the default instance may be overridden, as shown here.
* fabpowertasks inspects the variables for each Commands instance and attempts
to inject any matching values as described in ```injection_objs```. Any variables
that don't start with _ and are None as treated as potential injection points.
By default, an attempt to inject ```local_project_paths``` into every Commands instance
is made but more injections can be added using the **project_injection_objs** argument.

### Commands

The concept of Commands is simple - they are an advanced form of a Fabric Task.
Instead of being limited to the run() function, multiple functions of the
Command instance can be treated as Tasks.

#### Implementation

* Extend fabpowertasks.commands.BaseCommands
* Write the functions for your resulting Task
* ```__init__()```: Update self._task_functions with the functions
* ```__init__()```: Optionally, set instance variables for injection
* Import your new class into ```fabfile/__init__.py``` and pass into the
project_injection_objs dict where the resulting Tasks are auto-generated

Note that arguments to the function mirror what a standard Fabric task expects.
