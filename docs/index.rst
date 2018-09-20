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

Below 4 variables are required.

.. code-block:: text

    # AWS credentials
    aws_access_key_id = ''
    aws_secret_access_key = ''

    # AWS region
    region_name = 'us-west-2'

    # Amazon S3 staging directory where query results are stored.
    # NOTE: S3 should in the same region as specified above.
    # The format is 's3://<your s3 directory path>'
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