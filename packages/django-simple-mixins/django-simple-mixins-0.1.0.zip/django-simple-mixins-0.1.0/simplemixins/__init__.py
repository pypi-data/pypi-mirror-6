VERSION = (0, 1, 0)

def get_version():
    """ Return the Django Simple Mixins version as a string. """
    return '.'.join(map(str, VERSION))