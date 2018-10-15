Development Guide
===================

This is a guide for developers who would like to contribute to this project.


Fork this project
-------------------

Firstly, You need to fork this project and clone your fork into your computer.

.. code-block:: bash

    $ git clone <url-for-your-fork>

Local setup
--------------

The installation instructions in the README file are intended for users of athenacli. If you're developing athenacli, you'll need to install it in a slightly different way so you can see the effects of your changes right away without having to go through the install cycle everytime you change the code.

It is highly recommended to use pipenv for development. If you don't know what a pipenv is, `this guide <https://docs.python-guide.org/dev/virtualenvs/#virtual-environments>`_ will help you get started.

Suppose you have pipenv installed correctly and the current directory is in your local copy of athenacli, here are some useful commands:

.. code-block:: bash
    $ # install necessary dependences for both production and development
    $ pipenv install --dev 
    $ # active virtual environment
    $ pipenv shell
    $ # deactive virtual environment
    $ deactive
    $ # remove virtual environment for this project
    $ pipenv --rm

Running the tests
------------------

Currently we don't have enough tests for athenacli, because we haven't found an easy way to test AWS Athena locally, we have an `issue <https://github.com/dbcli/athenacli/issues/13>`_ track this problem. But we do have some unit tests for other parts, below are the steps to run them.

Make sure you have installed development dependences via `pipenv install --dev` and actived your virtual environment.

After that, tests can be run with:

.. code-block:: bash

    $ py.test

Create a pull request
------------------------

After making the changes and creating the commits in your local machine. Then push those changes to your fork. Then click on the pull request icon on github and create a new pull request. Add a description about the change and send it along. I promise to review the pull request in a reasonable window of time and get back to you.

In order to keep your fork up to date with any changes from mainline, add a new git remote to your local copy called 'upstream' and point it to the main athenacli repo.

.. code-block:: bash

    $ git remote add upstream https://github.com/dbcli/athenacli.git

Once the 'upstream' end point is added you can then periodically do a `git rebase <https://git-scm.com/docs/git-rebase>`_ to update your local copy.

