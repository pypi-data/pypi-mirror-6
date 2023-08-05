=====================
 nose_traceback_info
=====================

Have you ever wanted supplemental (debugging) info included in an
error or failure traceback produced by `nose`_? Do you find that
nose's `Failure Detail`_ plugin fails you (for example, because you
use `PyHamcrest`_ matchers)? Developing server software using Zope,
Plone, Paste or `WebError`_? Then this plugin might be the solution
you're looking for: it allows you to add whatever detailed information
you want to any frame in your traceback. Turn a traceback like this::

  Traceback (most recent call last):
  File "/.../nti.nose_traceback_info/src/nti/nose_traceback_info/tests/test_nose_traceback_info.py", line 39, in test_format_failure
    t, formatted, _ = self.plugin.formatFailure(None, exc_info)
  File "/.../nti.nose_traceback_info/src/nti/nose_traceback_info/__init__.py", line 48, in formatFailure
    return self.formatError( test, exc_info)
  File "/.../nti.nose_traceback_info/src/nti/nose_traceback_info/__init__.py", line 31, in formatError
    t, v, tb = exc_info
  TypeError: 'builtin_function_or_method' object is not iterable

into a traceback like this::

  TypeError: Traceback (most recent call last):
  Module unittest.case, line 331, in run
    testMethod()
  Module nti.nose_traceback_info.tests.test_nose_traceback_info, line 39, in test_format_failure
    t, formatted, _ = self.plugin.formatFailure(None, exc_info)
    - __traceback_info__: ("calling plugin with test and exc_info", None, <build-in function exc_info>)
  Module nti.nose_traceback_info, line 48, in formatFailure
    return self.formatError( test, exc_info)
  Module nti.nose_traceback_info, line 31, in formatError
    t, v, tb = exc_info
    - __traceback_info__: ("Test and exc_info args", None, <built-in function exc_info>)
  TypeError: 'builtin_function_or_method' object is not iterable


.. _Failure Detail: https://nose.readthedocs.org/en/latest/plugins/failuredetail.html
.. _nose: https://nose.readthedocs.org/en/latest/
.. _PyHamcrest: https://pyhamcrest.readthedocs.org
.. _WebError: https://pypi.python.org/pypi/WebError

Usage
=====

Once the plugin is installed (using ``pip`` or in a ``setup.py`` or
``requirements.txt`` file), it is enabled by default, just like
``logcapture.`` The plugin operates by looking for local variables in
each frame in a traceback and formatting them (both in captured logs
and tracebacks displayed for failured tests). The variables are
defined by conventions developed (and documented) by `Zope`_; these
conventions are also followed by `Paste`_ and `WebError`_, meaning
that information added to help debug tests can also be used to debug
production errors.

See that documentation for details on the variables. As a quick start,
the most important and most commonly used variable is
``__traceback_info__``, to which you can assign arbitrary information.
The ``repr`` of ``__traceback_info__`` is included in the traceback::

  def formatError(self, test, exc_info):
      __traceback_info__ = "Test and exc_info args", test, exc_info
      t, v, tb = exc_info


.. _paste: http://pythonpaste.org/modules/exceptions.html#module-paste.exceptions.collector
.. _zope: http://docs.zope.org/zope.exceptions/api.html

Options
-------

In addition to the standard environment variable and flags to enable
the plugin, additional options control some behaviour.

``--traceback-long-filenames``
  Use complete filenames, not module names, in formatted
  tracebacks.
``--traceback-nologcapture``
  Do not format tracebacks captured in logs.

Other Plugins
=============

This plugin is known to cooperate correctly with `nose-progressive`_,
which also adjusts the traceback.

.. _nose-progressive: https://pypi.python.org/pypi/nose-progressive/
