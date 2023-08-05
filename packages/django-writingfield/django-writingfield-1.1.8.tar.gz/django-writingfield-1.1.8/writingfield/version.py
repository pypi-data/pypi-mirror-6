from os import path
import json


def get_version():
    """returns a pep compliant version number"""

    fp = open(
        path.join(
            path.dirname(path.abspath(__file__)),
            'version.json'
        )
    )
    package = json.load(fp)
    fp.close()
    return package['version']
