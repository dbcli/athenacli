(Unreleased; add upcoming change notes here)
==============================================

1.6.2
=========

Features:
----------
* Add `--table-format` to change format used in `-e` mode. (Thanks: @ptshrdn)

1.6.1
=========

Bugfix:
----------
* update cursor.execution_time_in_millis to cursor.engine_execution_time_in_millis as libary PyAthena removed execution_time_in_millis

1.6.0
=========

Features:
----------
* Add support for configuring Athena workgroup ((Thanks: @warfox))

1.5.0
=========

Features:
----------
* Add homebrew installation support. ((Thanks: @chenrui333))
* Add a load command to load and execute a SQL file while in the REPL. (Thanks: @sco11morgan)

1.4.1
=========

Bugfix
----------
* Fix bug: athenaclirc not found if not in path. ((Thanks: @pdpark))

1.4.0
=========

Features:
----------
* Add support for `role_arn` in athenaclirc file to allow connection to assume aws role. (Thanks: @pdpark)
* Allow using an empty `--athenaclirc=` to not generate the default config file on first start (Thanks: @jankatins)
* Allow starting with `--profile=<aws_profile_name>` without having a corresponding entry in the `athenaclirc` config
  file (Thanks: @jankatins)
* Add support for supplying the SQL query on stdin by using `-` (minus) as query string: `--execute=-`.
  (Thanks: @jankatins)

1.3.3
========

Features
----------
* Add support for `arn_role` in athenaclirc file to allow connection to assume aws role. (Thanks: @pdpark)

Internal:
----------
* deprecate python versions 2.7, 3.4, 3.5 (Thanks: @zzl0)

1.3.0
========

Features
----------
* Show query execution statistics, such as the amount of data scanned and the approximate cost. (Thanks: @pgr0ss)

1.2.0
========

Features
----------
* Add a download command to fetch query results to a local CSV. (Thanks: @pgr0ss)

1.1.3
========

Features
----------
* Add auto-complete support for `JOIN` and related keywords. (Thanks: @getaaron)

Bugfix
----------
* Fix bug when completing `ON parent.` clauses. (Thanks: @pgr0ss)

1.1.2
========

Internal
-----------
* Require prompt_toolkit>=2.0.6. (Thanks: @zzl0)

0.1.4
========

Bugfix
----------
* `distinct` keyword cause an unexpected exception. (Thanks: @zzl0)

0.1.3
========

Features
----------
* Add error message for missing configuration (Thanks: @jashgala)
* Add colors and pager to config file (Thanks: @zzl0)

Internal
----------

* Updated docs (Thanks: @jashgala)
* Add support for pipenv (Thanks: @Hourann)
* Set poll_interval of PyAthena to 0.2s, this will reduce the response time (Thanks: @zzl0)
* Add developer guide (Thanks: @zzl0)

0.1.2
========

Features
----------

* Support default credentials and configurations of aws cli (Thanks: [Zhaolong Zhu])
* Support multiple named profiles in addition to a default profile of AWS configurations (Thanks: [Zhaolong Zhu])
    * Note: this feature changes the format of athenaclirc, it's incompatible with the old one.

Internal
----------

* Add link of `python-prompt-toolkit` and fix some sentences (Thanks: [Joe Block])


0.1.1
========

First public release!
