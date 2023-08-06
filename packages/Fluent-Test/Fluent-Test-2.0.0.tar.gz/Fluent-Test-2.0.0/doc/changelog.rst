Change Log
==========

Version 2.0.0 (15-Feb-2014)
-------------
- Remove ``fluenttest.TestCase.patches`` attribute.

  The ``patches`` attribute was just a little too magical for my tastes and
  it wasn't really necessary.  Removing this attribute also removed the
  ``patch_name`` parameter to :class:`~fluenttest.TestCase.patch`.  The latter
  change actually simplifies things quite a bit since we no longer have to
  derive safe attribute names.

- Add :meth:`fluenttest.TestCase.destroy`
- Switch to semantic versioning
- Expose library version with ``__version__`` attribute
- Add Makefile to simplify development process
- Remove usage of tox

Version 1 (27-Jul-2013)
-----------------------
- Implements :class:`fluenttest.TestCase`
- Implements :class:`fluenttest.ClassTester`
