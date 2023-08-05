try:
    from widgets import FullScreenTextarea
except ImportError:
    pass

VERSION = (1, 1, 6)


def get_version():
    """returns a pep complient version number"""
    return '.'.join(str(i) for i in VERSION)
