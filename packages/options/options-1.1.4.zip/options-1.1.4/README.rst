options
=======

``options`` helps represent option and configuration data in
a clean, high-function way.  Changes to options can "overlay"
earlier or default
settings.

For most functions and classes, ``options``
is overkill.
Python's function arguments, ``*args``,
``**kwargs``, and inheritance patterns are elegant and sufficient
for 99.9% of all development situations.
``options``
is for the top 0.1%:

  * highly functional classes (or functions),
  * with many different features and options,
  * which might be adjusted or overriden at any time,
  * yet that need "reasonable" or "intelligent" defaults, and
  * that yearn for a simple, unobtrusive API.

In those cases, Python's simpler built-in, inheritance-based model
adds complexity. Non-trivial options and argument-management
code spreads through many individual methods. This is where
``options``'s layered, delegation-based approach begins to shine.

.. image:: http://d.pr/i/6JI4+
    :align: center

For more backstory, see `this StackOverflow.com discussion of how to combat "configuration sprawl"
<http://stackoverflow.com/questions/11702437/where-to-keep-options-values-paths-to-important-files-etc/11703813#11703813>`_.
``options`` full documentation
can be found at `Read the Docs <http://options.readthedocs.org/en/latest/>`_. For examples of ``options``
in use, see `say <https://pypi.python.org/pypi/say>`_ and `show <https://pypi.python.org/pypi/show>`_.
