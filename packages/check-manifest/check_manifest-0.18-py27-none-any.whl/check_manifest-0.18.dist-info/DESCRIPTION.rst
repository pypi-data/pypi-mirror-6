check-manifest
==============

|buildstatus|_ |coverage|_

Are you a Python developer?  Have you uploaded packages to the Python Package
Index?  Have you accidentally uploaded *broken* packages with some files
missing?  If so, check-manifest is for you.

Quick start
-----------

::

    $ pip install check-manifest

    $ cd ~/src/mygreatpackage
    $ check-manifest

You can ask the script to help you update your MANIFEST.in::

    $ check-manifest -u
    listing source files under version control: 6 files and directories
    building an sdist: check-manifest-0.7.tar.gz: 4 files and directories
    files in version control do not match the sdist!
    missing from sdist:
      tests.py
      tox.ini
    suggested MANIFEST.in rules:
      include *.py
      include tox.ini
    updating MANIFEST.in

    $ cat MANIFEST.in
    include *.rst

    # added by check_manifest.py
    include *.py
    include tox.ini


Command-line reference
----------------------

::

    $ check-manifest --help
    usage: check-manifest [-h] [--version] [-c] [-u] [-p PYTHON]
                          [--ignore patterns]
                          [source_tree]

    Check a Python MANIFEST.in file for completeness

    positional arguments:
      source_tree           location for the source tree (default: .)

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -c, --create          create a MANIFEST.in if missing (default: False)
      -u, --update          append suggestions to MANIFEST.in (implies --create)
                            (default: False)
      -p PYTHON, --python PYTHON
                            use this Python interpreter for running setup.py sdist
                            (default: /home/mg/.venv/bin/python)
      --ignore patterns     ignore files/directories matching these comma-
                            separated patterns (default: None)


Configuration
-------------

You can tell check-manifest to ignore certain file patterns by adding a
``check-manifest`` section to your package's ``setup.cfg``.  Example::

    [check-manifest]
    ignore =
        .travis.yml

The following options are recognized:

ignore
    A list of newline separated filename patterns that will be ignored by
    check-manifest.  Use this if you want to keep files in your version
    control system that shouldn't be included in your source distributions.
    The default ignore list is ::

        PKG-INFO
        *.egg-info
        *.egg-info/*
        setup.cfg
        .hgtags
        .hgignore
        .gitignore
        .bzrignore
        *.mo

ignore-default-rules
    If set to ``true``, your ``ignore`` patterns will replace the default
    ignore list instead of adding to it.


.. |buildstatus| image:: https://api.travis-ci.org/mgedmin/check-manifest.png?branch=master
.. _buildstatus: https://travis-ci.org/mgedmin/check-manifest

.. |coverage| image:: https://coveralls.io/repos/mgedmin/check-manifest/badge.png?branch=master
.. _coverage: https://coveralls.io/r/mgedmin/check-manifest



Changelog
=========


0.18 (2014-01-30)
-----------------

* Friendlier error message when an external command cannot be found
  (`issue #21 <https://github.com/mgedmin/check-manifest/issues/21>`__).
* Add suggestion pattern for `.coveragerc`.
* Python 2.6 support
  (`issue #22 <https://github.com/mgedmin/check-manifest/issues/22>`__).


0.17 (2013-10-10)
-----------------

* Read the existing MANIFEST.in file for files to ignore
  (`issue #19 <https://github.com/mgedmin/check-manifest/issues/19>`__).


0.16 (2013-10-01)
-----------------

* Fix Subversion status parsing in the presence of svn usernames longer than 12
  characters (`issue #18 <https://github.com/mgedmin/check-manifest/issues/18>`__).


0.15 (2013-09-20)
-----------------

* Normalize the paths of all files, avoiding some duplicate misses of
  directories.  (`issue #16 <https://github.com/mgedmin/check-manifest/issues/16>`__).
  [maurits]


0.14 (2013-08-28)
-----------------

* Supports packages that do not live in the root of a version control
  repository (`issue #15 <https://github.com/mgedmin/check-manifest/issues/15>`__).

* More reliable svn support: detect files that have been added but not
  committed (or committed but not updated).

* Licence changed from GPL (v2 or later) to MIT
  (`issue #12 <https://github.com/mgedmin/check-manifest/issues/12>`__).


0.13 (2013-07-31)
-----------------

* New command line option: --ignore
  (`issue #11 <https://github.com/mgedmin/check-manifest/issues/11>`__).
  Contributed by Steven Myint.

* New command line option: -p, --python.  Defaults to the Python you used to
  run check-manifest.  Fixes issues with packages that require Python 3 to run
  setup.py (`issue #13 <https://github.com/mgedmin/check-manifest/issues/13>`__).


0.12 (2013-05-15)
-----------------

* Add suggestion pattern for `Makefile`.

* More generic suggestion patterns, should cover almost anything.

* zest.releaser_ integration: skip check-release for non-Python packages
  (`issue #9 <https://github.com/mgedmin/check-manifest/issues/9>`__).


0.11 (2013-03-20)
-----------------

* Make sure ``MANIFEST.in`` is not ignored even if it hasn't been added to the
  VCS yet (`issue #7 <https://github.com/mgedmin/check-manifest/issues/7>`__).


0.10 (2013-03-17)
-----------------

* ``check-manifest --version`` now prints the version number.

* Don't apologize for not adding rules for directories (especially after adding
  rules that include files inside that directory).

* Python 3 support contributed by Steven Myint.

* Default ignore patterns can be configured in ``setup.cfg``
  (`issue #3 <https://github.com/mgedmin/check-manifest/issues/3>`_).


0.9 (2013-03-06)
----------------

* Add suggestion pattern for `.travis.yml`.

* When check-manifest -u (or -c) doesn't know how to write a rule matching a
  particular file, it now apologizes explicitly.

* Copy the source tree to a temporary directory before running python setup.py
  sdist to avoid side effects from setuptools plugins or stale
  \*.egg-info/SOURCES.txt files
  (`issue #1 <https://github.com/mgedmin/check-manifest/issues/1>`_).

* Warn if `*.egg-info` or `*.mo` is actually checked into the VCS.

* Don't complain if `*.mo` files are present in the sdist but not in the VCS
  (`issue #2 <https://github.com/mgedmin/check-manifest/issues/2>`_).


0.8 (2013-03-06)
----------------

* Entry point for zest.releaser_.  If you install both zest.releaser and
  check-manifest, you will be asked if you want to check your manifest during
  ``fullrelease``.

.. _zest.releaser: https://pypi.python.org/pypi/zest.releaser


0.7 (2013-03-05)
----------------

* First release available from the Python Package Index.

* Moved from https://gist.github.com/4277075
  to https://github.com/mgedmin/check-manifest

* Added README.rst, CHANGES.rst, setup.py, tox.ini (but no real tests yet),
  MANIFEST.in, and a Makefile.

* Fixed a bug in error reporting (when setup.py failed, the user would get
  `TypeError: descriptor '__init__' requires a 'exceptions.Exception' object
  but received a 'str'`).


