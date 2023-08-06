=======
CHANGES
=======

4.1.4 (2014-03-19)
------------------

- Added support for Python 3.4.

- Updated ``bootstrap.py`` to version 2.2.

4.1.3 (2013-03-12)
------------------

- Fixed interface object introspection in PyPy. For some reason PyPy made
  attributes available despite the restrictive ``__slots__`` declaration.

- Added a bunch of tests surrounding interface lookup and adaptation.

4.1.2 (2013-03-11)
------------------

- Fixed ``PyProxyBase.__iter__()`` to return the result of
  ``PyProxyBase._wrapped.__iter__`` if available, otherwise fall back to
  Python internals. The previous implementation always created a generator.

- Fixed ``PyProxyBase.__setattr__()`` to allow setting of properties on the
  proxy itself. This is needed to properly allow proxy extensions as was
  evidenced int he ``zope.security.decorator`` module.

4.1.1 (2012-12-31)
------------------

- Fleshed out PyPI Trove classifiers.

4.1.0 (2012-12-19)
------------------

- Enabled compilation of dependent modules under Py3k.

- Replaced use of ``PyCObject`` APIs with equivalent ``PyCapsule`` APIs,
  except under Python 2.6.

  N.B.  This change is an ABI incompatibility under Python 2.7:
        extensions built under Python 2.7 against 4.0.x versions of
        ``zope.proxy`` must be rebuilt.

4.0.1 (2012-11-21)
------------------

- Added support for Python 3.3.

4.0.0 (2012-06-06)
------------------

- Added support for PyPy.

  N.B.:  the C extension is *not* built under PyPy.

- Added a pure-Python reference / fallback implementations of
  ``zope.proxy.ProxyBase`` and the proxy module API functions.

  N.B.:  the pure-Python proxy implements all regular features of
  ``ProxyBase``;  however, it does not exclude access to the wrapped object
  in the same way that the C version does.  If you need that information
  hiding (e.g., to implement security sandboxing), you still need to use
  the C version.

- Added support for continuous integration using ``tox`` and ``jenkins``.

- 100% unit test coverage.

- Added Sphinx documentation:  moved doctest examples to API reference.

- Added 'setup.py docs' alias (installs ``Sphinx`` and dependencies).

- Added 'setup.py dev' alias (runs ``setup.py develop`` plus installs
  ``nose`` and ``coverage``).

- Replaced deprecated ``zope.interface.implements`` usage with equivalent
  ``zope.interface.implementer`` decorator.

- Dropped support for Python 2.4 and 2.5.

- Added Python 3.2 support.

3.6.1 (2010-07-06)
------------------

- Make tests compatible with Python 2.7.

3.6.0 (2010-04-30)
------------------

- Removed test extra and the remaining dependency on zope.testing.

- Removed use of 'zope.testing.doctestunit' in favor of stdlib's 'doctest.

3.5.0 (2009/01/31)
------------------

- Added support to bootstrap on Jython.

- Use zope.container instead of zope.app.container.

3.4.2 (2008/07/27)
------------------

- Made C code compatible with Python 2.5 on 64bit architectures.

3.4.1 (2008/06/24)
------------------

- Bug: Updated `setup.py` script to conform to common layout. Also updated
  some of the fields.

- Bug: The behavior of tuples and lists in the `__getslice__()` and
  `__setslice__()` method were incorrect by not honoring the pre-cooked
  indices. See http://docs.python.org/ref/sequence-methods.html.

3.4.0 (2007/07/12)
------------------

- Feature: Added a decorator module that supports declaring interfaces on
  proxies that get blended with the interfaces of the things they proxy.

3.3.0 (2006/12/20)
------------------

- Corresponds to the verison of the `zope.proxy` package shipped as part of
  the Zope 3.3.0 release.


3.2.0 (2006/01/05)
------------------

- Corresponds to the verison of the zope.proxy package shipped as part of
  the Zope 3.2.0 release.


3.0.0 (2004/11/07)
------------------

- Corresponds to the verison of the zope.proxy package shipped as part of
  the Zope X3.0.0 release.
