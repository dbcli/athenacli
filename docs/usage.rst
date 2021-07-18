
Usages
================

Options
-------------

.. code-block:: bash

    $ athenacli --help
    Usage: athenacli [OPTIONS] [DATABASE]

      A Athena terminal client with auto-completion and syntax highlighting.

      Examples:
        - athenacli
        - athenacli my_database

    Options:
      -e, --execute TEXT            Execute a command (or a file) and quit.
      -r, --region TEXT             AWS region.
      --aws-access-key-id TEXT      AWS access key id.
      --aws-secret-access-key TEXT  AWS secretaccess key.
      --s3-staging-dir TEXT         Amazon S3 staging directory where query
                                    results are stored.
      --work_group TEXT             Amazon Athena workgroup in which query is run,
                                    default is primary
      --athenaclirc FILE            Location of athenaclirc file.
      --profile TEXT                AWS profile
      --table-format TEXT           Table format used with -e option.
      --help                        Show this message and exit.

Connect to a database
------------------------

Connect a specific database with AWS credentials, region name and S3 staging
directory or work group. AWS credentials, region name and S3 staging directory
are optional. You can set those variables in `athenaclirc` config file, and then
run below command.

.. code-block:: bash

    $ athenacli ddbtablestats

Exit athenacli
------------------

Press `ctrl+d` or type `quit` or `exit`.

Special Commands
--------------------

Save 'SELECT user_id, tweet_id from twitterfeed LIMIT 2' as a favorite query called 'q1':

.. code-block:: bash

    > \fs q1 SELECT user_id, tweet_id from twitterfeed LIMIT 2

Run the named query:

.. code-block:: bash

    > \f q1

Execute a command (or a file)
---------------------------------

Execute a command and quit:

.. code-block:: bash

    $ athenacli -e 'show databases'

Execute a file and quit:

.. code-block:: bash

    $ athenacli -e examples/create_table.sql
