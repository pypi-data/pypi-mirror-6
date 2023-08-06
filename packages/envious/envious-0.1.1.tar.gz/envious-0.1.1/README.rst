Envious: Unleash the power of .env files
========================================

If you spend a lot of time switching between multiple Python projects and using
several virtual environment, you'll be familiar with the pain of injecting the
right environment variables into your scripts. You can use autoenv, but it
doesn't automatically load the virtual environment for you, so you need to
litter the .env file with bash commands. Or you can use a postactivate hook in
virtualenvwrapper, but that would mean not having a standardized,
default location for all the needed environment variables. And what if you use
an IDE like PyCharm, which doesn't load variables from .env files?

Envious solves the problem by loading configurations from an .env file in the
working directory directly from within your Python code, injecting environment
variables if they're not already defined, while keeping those that are already
set.


Installation
------------

To install envious, simply type:

.. code-block:: bash

    $ pip install envious


Usage
-----

To have your project import environment variables from an .env file, first
create the file in the root folder of your project:

.. code-block:: bash

    ENVIRONMENT=development
    MONGODB_URL=http://localhost:27017/mydb
    REDIS_URL=http://localhost:6379/0

Then add the following to the Python app entry point:

.. code-block:: pycon

    from envious import load_env

    load_env()

If you want to manage multiple configuration files for the same project, you're
covered. Create multiple configuration files, and then specify the one you want
to use by providing an environment variable named ``ENV_FILE``:

.. code-block:: bash

    $ echo MONGODB_URL=http://localhost:27017/myseconddb > .env2
    $ ENV_FILE=.env2 python my_script.py

The script will see the alternative value for the environment value
``MONGODB_URL``.