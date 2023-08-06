
Fluent Unit Testing
===================

    *"When a failing test makes us read 20+ lines of test code,
    we die inside."* - C.J. Gaconnet

This is an attempt to make Python testing more readable while maintaining a
Pythonic look and feel.  As powerful and useful as the `unittest`_ module is,
I've always disliked the Java-esque naming convention amongst other things.

While truly awesome, attempts to bring BDD to Python never feel *Pythonic*.
Most of the frameworks that I have seen rely on duplicated information between
the specification and the test cases.  My belief is that we need something
closer to what `RSpec`_ offers but one that feels like Python.

.. toctree::
   :maxdepth: 2

   unit-testing
   api
   changelog

.. include:: links.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _unittest: http://docs.python.org/2/library/unittest.html
.. _RSpec: http://rspec.info/
