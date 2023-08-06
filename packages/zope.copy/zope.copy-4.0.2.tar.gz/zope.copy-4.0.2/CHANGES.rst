=======
CHANGES
=======

4.0.2 (2014-03-19)
------------------

- Added support for Python 3,3 and 3.4.

- Updated ``boostrap.py`` to version 2.2.

4.0.1 (2012-12-31)
------------------

- Fleshed out PyPI Trove classifiers.

4.0.0 (2012-06-13)
------------------

- Added support for Python 3.2.

- Dropped ``zope.component`` as a testing requirement. Instead, register
  explicit (dummy) adapter hooks where needed.

- Added PyPy support.

- 100% unit test coverage.

- Added support for continuous integration using ``tox`` and ``jenkins``.

- Added Sphinx documentation:  moved doctest examples to API reference.

- Added 'setup.py docs' alias (installs ``Sphinx`` and dependencies).

- Added 'setup.py dev' alias (runs ``setup.py develop`` plus installs
  ``nose``, ``coverage``, and testing dependencies).

- Dropped support for Python 2.4 and 2.5.

- Include tests of the LocationCopyHook from zope.location.

3.5.0 (2009-02-09)
------------------

- Initial release. The functionality was extracted from ``zc.copy`` to
  provide a generic object copying mechanism with minimal dependencies.
