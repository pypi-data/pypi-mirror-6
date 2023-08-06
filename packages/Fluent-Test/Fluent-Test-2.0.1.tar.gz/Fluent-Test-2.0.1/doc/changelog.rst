Change Log
==========

Version 2.0.1 (15-Feb-2014)
---------------------------
- Correct a packaging version defect.

  *Setup.py* cannot safely retrieve the version from the ``__version__``
  attribute of the package since the import requires ``mock`` to be
  present.  The immediate hot-fix is to duplicate the version number
  until I can come up with a cleaner solution.

Version 2.0.0 (15-Feb-2014)
---------------------------
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
