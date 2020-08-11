Install
============

Pip
----------------

If you already know how to install python packages, then you can do:

.. code-block:: bash

    $ pip install athenacli

You might need sudo, or you can install it in a virtualenv.

Docker
---------

If you already know how to use docker, then you can do:

.. code-block:: bash

    $ docker run --rm -ti -v $(pwd):/home/athena zzl0/athenacli athenacli

Note: we map the home directory (`/home/athena`) of docker container to current directory, `athenacli` will create a config file in it (`.athenacli/athenaclirc`), you might need to change some variables (please refer to `quick start` section of :doc:`index` page).

MacOS
---------

For MacOS users, you can also use Homebrew to install it:

.. code-block:: bash

    $ brew install athenacli
