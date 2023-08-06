options
=======

``options`` helps encapsulate options and configuration data using a
layered stacking model (a.k.a. nested contexts).

For most functions and many classes, ``options``
is overkill and not recommended.
Python's already-flexible function arguments, ``*args``,
``**kwargs``, and inheritance patterns are elegant and sufficient
for 99.9% of all development situations.
``options``
is for the other 0.1%: 

  * highly functional classes, 
  * with many different features and options, 
  * which might be adjusted or overriden at any time,
  * yet that need "reasonable" or "intelligent" defaults, and
  * that yearn for a simple, unobtrusive API.

In those cases, Python's simpler built-in, inheritance-based model
adds complexity as non-trivial options and argument-management
code spreads through many individual methods. This is where
``options``'s delegation-based approach begins to shine.

.. image:: http://d.pr/i/6JI4+
    :align: center


.. image:: https://pypip.in/d/options/badge.png
    :target: https://crate.io/packages/options/


For more backstory, see `this StackOverflow.com discussion of how to combat "configuration sprawl"
<http://stackoverflow.com/questions/11702437/where-to-keep-options-values-paths-to-important-files-etc/11703813#11703813>`_.
``options`` full documentation
can be found at `Read the Docs <http://options.readthedocs.org/en/latest/>`_. For examples of ``options``
in use, see `say <https://pypi.python.org/pypi/say>`_ and `show <https://pypi.python.org/pypi/show>`_.
