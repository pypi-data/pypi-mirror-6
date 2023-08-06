import os

__author__ = 'Matteo Danieli'


def load_env():
    """Load environment variables from a .env file, if present.

    If an .env file is found in the working directory, and the listed
    environment variables are not already set, they will be set according to
    the values listed in the file.
    """
    try:
        variables = open('.env').read().splitlines()
        for v in variables:
            if '=' in v:
                key, value = v.split('=')
                if not key in os.environ:
                    os.environ[key] = value
    except IOError:
        pass
