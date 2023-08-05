Introduction
============

This library provides a Python wrapper for Veracity's command-line interface.
It includes objects for repositories, working copies, and other commonly-used
items. The library also installs several command-line tools to work with
Veracity's distributed build tracking features.

.. NOTE::
   0.0.x releases are experimental and interfaces will likely change.



Getting Started
===============

Requirements
------------

* Python 3.3

* Veracity 2.5


Dependencies
------------

* sh: https://pypi.python.org/pypi/sh (subprocess wrapper for Mac/Linux)

* pbs: https://pypi.python.org/pypi/pbs (subprocess wrapper for Windows)

* virtualenv: https://pypi.python.org/pypi/virtualenv (isolated builds)


Installation
------------

The package can be installed using ``pip``::

    pip install python-veracity

or directly from source::

    python setup.py install

After installation, it is available under the name ``veracity``::

    >>> import veracity
    >>> veracity.__version__

    >>> from veracity import vv
    >>> vv.version()
    >>> vv.repos()



Scripting Interface
===================

A sample script might look similar to the following::

    #!/usr/bin/env python

    from veracity import Repository, WorkingCopy, Item

    # Clone a repo
    repo = Repository('veracity', remote='http://public.veracity-scm.com/repos/veracity')

    # Display Repository attributes
    print repo.name
    print repo.users
    print repo.branches
    print repo.tags

    # Check out a working copy (from a Repository)
    work = repo.checkout("~/v/veracity")
    work.delete()

    # Check out a working copy (by repo name)
    work = WorkingCopy("~/v/veracity", repo='veracity')
    work.update(branch='master')

    # Change some files
    item = Item('docs/GettingStarted.txt', work=work)
    item.lock()



Build Tracking
==============

This package also installs a set of command-line tools to work with Veracity's
Build Tracking feature: http://veracity-scm.com/qa/questions/123

Configuration
-------------

In your master branch, create a ``setup.cfg`` similar to the following::

   [vv-tracking]

   repositories = python-veracity
   series = N, C
   environments = W, M, L
   virtualenv = True


   [vv-poller]

   N_branches = *
   N_command = [ $( date "+%H" ) = 00 ]
   N_command-nt = if %TIME:~0,2%==00 (exit /b 0) else (exit /b 1)
   N_sleep = 60 * 30
   N_start = Q

   C_branches = master, develop, feature-*, release-*, hotfix-*
   C_sleep = 60
   C_start = Q


   [vv-builder]

   U_enter = Q
   U_path = .
   U_command = make depends
   U_fail = UF

   B_enter = U
   B_path = .
   B_command = make install
   B_fail = BF

   T_enter = B
   T_path = .
   T_command = make test
   T_fail = TF

   C_enter = T
   C_path = .
   C_command = make check
   C_fail = CF
   C_exit = D

The series, environments, and statuses must match what is defined in your
repository's build configuration page: http://SERVER.com/repos/REPO/build-setup


Poller
------

To run one iteration of a poller for your repository::

    vv-poller <repository names>

Or, to run forever as a daemon::

    vv-poller <repository names> --daemon

From within a working copy, the poller configuration can be tested using::

    vv-poller --test


Builder
-------

To run one iteration of a builder for your repository::

    vv-builder <repository names> --env <environment alias>

Or, to run forever as a daemon::

    vv-builder <repository names> --env <environment alias> --daemon

From within a working copy, the builder configuration can be tested using::

    vv-builder --test
