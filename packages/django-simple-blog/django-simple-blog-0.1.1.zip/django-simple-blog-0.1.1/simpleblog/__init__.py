VERSION = (0, 1, 1)

def get_version():
    """Return the Django Simple Blog version as a string."""
    return '.'.join(map(str, VERSION))