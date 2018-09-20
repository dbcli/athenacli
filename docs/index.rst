AthenaCLI
==========

AthenaCLI is a command line client for `Athena <https://aws.amazon.com/athena/>`_ service that can do auto-completion and syntax highlighting, and is a proud member of the dbcli community.

.. figure:: _static/gif/athenacli.gif
    :align: center

* Source: https://github.com/dbcli/athenacli

Quick Start
=============

Install
-------------

    $ pip install athenacli

Config
------------

A config file is automatically created at ~/.athenacli/athenaclirc at first launch (run `athenacli`). See the file itself for a description of all available options.

Below 3 variables are required.

.. code-block:: text

    # AWS credentials
    aws_access_key_id = ''
    aws_secret_access_key = ''

    # Amazon S3 staging directory where query results will be stored.
    s3_staging_dir = ''

Create a table
---------------

    $ athenacli -e examples/create_table.sql

Run a query
--------------

    $ athenacli -e 'select elb_name, request_ip from elb_logs LIMIT 10'

REPL
-------------

    $ athenacli [<database_name>]


Table of Contents
-----------------

.. toctree::

   features
   usage
   faq