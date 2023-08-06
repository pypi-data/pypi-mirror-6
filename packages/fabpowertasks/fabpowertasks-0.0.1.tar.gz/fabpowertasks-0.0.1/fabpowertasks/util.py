"""
Utility functions
"""


def convert_to_cmd_options(args=None, options=None):
    """
    Converts the given list of args and dict of options to a string expected for
    standard Unix-like command line options
    e.g. [arg, ...] [--kwarg=val, --kwarg-arg=val2, ...]

    :param args:
    :param options:
    """
    args = args or []
    options = options or {}

    cmd_parts = []
    cmd_parts.extend(args)

    for key, value in options.iteritems():
        cmd_parts.append('--%s' % key.replace('_', '-'))
        cmd_parts.append(value)

    return ' '.join(cmd_parts)


def is_truthy(data):
    """
    Returns True if the data is a truthy value, False otherwise.
    """
    string = str(data).lower()
    return string in ['true', '1', 'f']
