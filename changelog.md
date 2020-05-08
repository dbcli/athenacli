(Unreleased; add upcoming change notes here)
==============================================

Features:
----------
* Add support for `role_arn` in athenaclirc file to allow connection to assume aws role. (Thanks: @pdpark)

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
