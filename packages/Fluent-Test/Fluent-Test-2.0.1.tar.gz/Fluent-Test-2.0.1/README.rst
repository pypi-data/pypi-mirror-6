Fluent Unit Testing
===================

*Readable hybrid testing*

Why?
~~~~

This is an attempt to make Python testing more readable while maintaining a
Pythonic look and feel.  As powerful and useful as the `unittest`_ module is,
I've always disliked the Java-esque naming convention amongst other things.

While truly awesome, attempts to bring BDD to Python never feel *Pythonic*.
Most of the frameworks that I have seen rely on duplicated information between
the specification and the test cases.  My belief is that we need something
closer to what `RSpec`_ offers but one that feels like Python.

Where?
~~~~~~

- Source Code: https://github.com/dave-shawley/fluent-test
- CI: https://travis-ci.org/dave-shawley/fluent-test
- Documentation: https://fluent-test.readthedocs.org/

Contributing
~~~~~~~~~~~~

Fluent-test uses Vincent Driessen's excellent `gitflow`_ extenion to manage
work flow through github.  Contributions are welcome as long as they follow
a few basic rules:

1. They start out life by forking the central repo and creating a new
   feature branch named *feature/my-feature* from the *develop* branch.
2. All tests pass and coverage is at 100% - **make test**
3. All quality checks pass - **make lint**
4. Issue a pull-request through github.

Development Environment
-----------------------

Like many other projects, the development environment is contained in a
virtual environment and controlled by a Makefile.  The inclusion of make is
less than perfect, but it is the easiest way to bootstrap a project on just
about any platform.  Start out by cloning the repository with git and
building a virtual environment to work with::

    $ git clone https://github.com/my-org/fluent-test.git
    $ cd fluent-test
    $ make environment

This will create a Python 3 environment in the *env* directory using mkvenv
and install the various prerequisites such as *pip* and *nose*.  You can
activate the environment source ``source env/bin/activate``, launch a Python
interpreter with ``env/bin/python``, and run the test suite with ``env/bin/nosetests``.

The Makefile exports a few other useful targets:

- **make test**: run the tests
- **make lint**: run various static analysis tools
- **make clean**: remove cache files
- **make mostly-clean**: remove built and cached eggs
- **make dist-clean**: remove generated distributions
- **make maintainer-clean**: remove virtual environment
- **make sdist**: create a distribution tarball
- **make docs**: build the HTML documentation

.. _unittest: http://docs.python.org/2/library/unittest.html
.. _RSpec: http://rspec.info/
.. _gitflow: https://github.com/nvie/gitflow
