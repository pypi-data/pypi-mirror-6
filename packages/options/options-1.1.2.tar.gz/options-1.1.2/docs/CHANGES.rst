Change Log
==========

1.1 (October 29, 2103)
''''''''''''''''''''''''

  * Added ``OptionsClass`` base class. If client classes inherit
    from this, they automatically get ` set()`` and ``settings()``
    methods.

1.0.7 (October 25, 2103)
''''''''''''''''''''''''

  * Mainly doc tweaks.

1.0.4 - 1.0.6 (October 24, 2013)
''''''''''''''''''''''''''''''''
  
* When bad option names are defined ("bad" here meaning "conflicts with
        names already chosen for pre-existing methods"), a ``BadOptionName``
    exception will be raised.
  * Tweaked docs, adding comparison chart.

1.0.3 (September 23, 2013)
''''''''''''''''''''''''''

  * Switched to local version of ``chainstuf`` until bug
    with generator values in
    ``stuf.chainstuf`` can be tracked down and corrected.
    This was blocking a downstream feature-release of ``say``.

1.0.2 (September 19, 2013)
''''''''''''''''''''''''''

  * Improved ``setdefault`` and ``update`` methods, and added tests,
    primarily in effort to work around bug that appears in ``stuf``,
    ``orderedstuf``, or ``chainstuf`` when a mapping value is a
    generator.
  * Documentation improved.

1.0.1 (September 2013)
''''''''''''''''''''''

  * Moved main documentation to Sphinx format in ./docs, and hosted
    the long-form documentation on readthedocs.org. README.rst now
    an abridged version/teaser for the module.

1.0 (Septemer 2013)
'''''''''''''''''''

  * Cleaned up source for better PEP8 conformance
  * Bumped version number to 1.0 as part of move to `semantic
    versioning <http://semver.org>`_, or at least enough of it so
    as to not screw up Python installation procedures (which don't
    seem to understand 0.401 is a lesser version that 0.5, because
    401 > 5).
