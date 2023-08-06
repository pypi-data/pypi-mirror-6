Third Party Tangled Extensions
==============================

.. image:: https://travis-ci.org/TangledWeb/tangled.contrib.png?branch=master
   :target: https://travis-ci.org/TangledWeb/tangled.contrib

``tangled.contrib`` is a namespace package for third party Tangled extensions.
The layout for such an extension looks like this::

    ${project root}/
        setup.py
        README
        tangled/ (empty directory)
            contrib/ (empty directory)
                ${package name}/
                    __init__.py

The ``tangled scaffold`` command can be used to create such a package::

    tangled scaffold contrib tangled.contrib.sqlalchemy

.. note:: The ``tangled.contrib`` namespace can be used by anyone, but please
          don't name your package ``tangled.{name}``--the top level ``tangled``
          namespace is reserved for official packages.

This will create the following directories and files in the directory where the
command was run::

    tangled.contrib.sqlalchemy/
        setup.py
        README
        tangled/
            contrib/
                sqlalchemy/
                    __init__.py

`Documentation <http://tangledframework.org/docs/tangled.contrib/>`_
