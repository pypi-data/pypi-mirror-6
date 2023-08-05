_version = (1, 3, 15)


def get_version():
    """returns a pep complient version number"""
    return '.'.join(str(i) for i in _version)

VERSION = get_version()
