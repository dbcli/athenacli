AWS Configs
===================

AthenaCLI tries to reuse the AWS credentials and configurations configured by `AWS CLI <https://docs.aws.amazon.com/cli/latest/topic/config-vars.html#cli-aws-help-config-vars>`_.

Precedence
---------------

The AthenaCLI looks for credentials and configuration settings in the following order:

1. **Command line options** – aws-access-key-id, aws-secret-access-key, region, s3-staging-dir, work-group can be specified as command options to override default settings.
2. **AthenaCLI config file** – typically located at `~/.athenacli/athenaclirc` on Linux, macOS, or Unix. This file can contain multiple named profiles in addition to a default profile. Just adds `--profile [PROFILE_NAME]` at the end of athenacli command to use those configurations.
3. **Environment variables** – AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, AWS_ATHENA_S3_STAGING_DIR, AWS_ATHENA_WORK_GROUP
4. **AWS credentials file** – located at `~/.aws/credentials` on Linux, macOS, or Unix. This file can contain multiple named profiles in addition to a default profile. Please refer to `AWS CLI` for more information.
5. **AWS CLI config file** – typically located at `~/.aws/config` on Linux, macOS, or Unix. This file can contain multiple named profiles in addition to a default profile. Please refer to `AWS CLI` for more information.

* **Note:** *Whether or not a particular value will be used from a given option above depends on the truthyness of the values. e.g. if the `aws_access_key_id` field is present in the AthenaCLI config file, but its value is empty, it will not be considered (since the truthyness of an empty string is False) and the program will try to resolve to the next available option.*

Available configs
------------------------------------

Some variables are not available in all the config files, below table lists the config files in which you can set a variable.

+-----------------------+---------------------------+---------------------+
| **Variable**          | **Environment Variable**  | **Available files** |
+-----------------------+---------------------------+---------------------+
| aws_access_key_id     | AWS_ACCESS_KEY_ID         | - AthenaCLI config  |
|                       |                           | - AWS credentials   |
|                       |                           | - AWS CLI config    |
+-----------------------+---------------------------+---------------------+
| aws_secret_access_key | AWS_SECRET_ACCESS_KEY     | - AthenaCLI config  |
|                       |                           | - AWS credentials   |
|                       |                           | - AWS CLI config    |
+-----------------------+---------------------------+---------------------+
| token                 | AWS_SESSION_TOKEN         | N/A                 |
+-----------------------+---------------------------+---------------------+
| region                | AWS_DEFAULT_REGION        | - AthenaCLI config  |
|                       |                           | - AWS CLI config    |
+-----------------------+---------------------------+---------------------+
| s3_staging_dir        | AWS_ATHENA_S3_STAGING_DIR | - AthenaCLI config  |
+-----------------------+---------------------------+---------------------+
| work_group            | AWS_ATHENA_WORK_GROUP     | - AthenaCLI config  |
+-----------------------+---------------------------+---------------------+
