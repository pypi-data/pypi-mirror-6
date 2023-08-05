"""Reflection tools for inspecting Python objects and code.


Glossary
--------
This module uses the following terminology:

.. note:: **TODO:**
    move these terms to a global glossary and reference them here

.. glossary::
    :sorted:

    directory name
        The name of a directory.  This is the last slash-delimited
        component of the directory's :term:`path <directory path>`.

        Example: The name of :file:`/usr/lib` is :file:`lib`.

    directory path
        A path that can be used to reference a directory in a file
        system.

        Example: :file:`/usr/lib`

    file extension
        A type- or purpose-identifying suffix in a :term:`file name`.
        It usually starts with a period.

        Examples:
            * The extension of :file:`module.pyc` is ``.pyc``.
            * The extension of :file:`.bashrc` is ``rc``.

    file name
        The name of a file.  This is the last slash-delimited component
        of the file's :term:`path <file path>`.

        Example: The name of :file:`/usr/bin/python` is :file:`python`.

    file path
        A path that can be used to reference a file in a file system.

        Example: :file:`/usr/bin/python`

    included module
        In the context of some current module, another module *M* whose
        entire public interface is provided as part of the current
        module via :samp:`from {M} import *`.

    init module
        A module that, when placed in a directory, designates that
        directory as a Python package.  It is loaded when the package is
        loaded.  Typically it populates the package's namespace.

        Init modules have one of the following :term:`file name`\ s:
        :file:`__init__.py`, :file:`__init__.pyc`, :file:`__init__.pyo`,
        or :file:`__init__.pyd`.

    metatype
        A category of Python types.  One of {``oldstyle``, ``function``,
        ``class``, ``module``}.

    module name
        The name of a module.  This is the last period-delimited
        component of the module's :term:`path <module path>`.  It is
        also the module's :term:`file name` sans :term:`file extension`.

        Example: The name of :mod:`os.path` is :mod:`!path`.

    module path
        A path that can be used to reference a module in Python.

        Example: :mod:`!os.path`

    object name
        The name of an object.  This is the last period-delimited
        component of the object's :term:`path <object path>`.

        Example: The name of :func:`os.path.join` is ``join``.

    object path
        A path that can be used to reference an object in Python.

        Example: ``os.path.join``

    package name
        The name of a package.  This is the last period-delimited
        component of the package's :term:`path <package path>`.  It is
        also the package's :term:`directory name`.

        Example: The name of :mod:`spruce.introspect` is
        :mod:`!introspection`.

    package path
        A path that can be used to reference a package in Python.

        Example: :mod:`!spruce.introspect`

    parent module
        The module within whose namespace a named object is defined.
        Note that the same object may actually have distinct named
        identities in multiple namespaces.  The parent module is defined
        with respect to each named identity.

        Example: The parent of :func:`os.path.join` is :mod:`os.path`.

    parent object
        In the context of some current object, the object of which the
        current object is an attribute.

        Example: The parent of :meth:`!list.append` is :obj:`list`.

    top-level object
        In the context of a module, an object in the module's global
        namespace.

"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__credits__ = ["Ivan D Vasin"]
__maintainer__ = "Ivan D Vasin"
__email__ = "nisavid@gmail.com"
__docformat__ = "restructuredtext"

from ._attrs import *
from ._exc import *
from ._imp import *
from ._modules import *
from ._objects import *
from ._paths import *
