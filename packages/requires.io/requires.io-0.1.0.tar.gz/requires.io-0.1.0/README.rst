requires.io API
---------------

.. image:: https://requires.io/github/requires/api/requirements.png?branch=master
   :target: https://requires.io/github/requires/api/requirements/?branch=master
   :alt: Requirements Status

Install:

.. code::

    pip install requires.io

Quick start:

.. code::

    requires.io -a my_auth_token -r my_repo /path/to/my/repo

Usage:

.. code::

    requires.io [options] path ...

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -a TOKEN, --auth-token=TOKEN
                            API token.
      -r NAME, --repository=NAME
                            repository name.
      -p, --private         is the repository private? (default: false)
      -b NAME, --branch=NAME
                            branch or tag name. (default: master)
      -t, --tag             does the branch name stand for a tag? (default: false)

