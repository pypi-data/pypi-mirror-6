from widgets import FullScreenTextarea

VERSION = (1, 1, 2)


def get_version():
    """returns a pep complient version number"""
    return '.'.join(str(i) for i in VERSION)
