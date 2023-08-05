"""Modules, packages, and module paths.

Python's module objects already provide some degree of introspection.
But these objects are only created when the modules are imported.  A
number of limitations arises as a result.  For example, it is not
straightforward to inspect modules that are not installed or modules
that are known only by :term:`file name`.

The tools in this module are designed to address these limitations.  The
representations defined here can be easily created from :term:`module
path`\ s, :term:`file path`\ s, or Python module objects.  There are
also functions and methods that list the modules available in a file
system directory or in a package.

Unless otherwise noted, when these tools are documented as handling
"modules" or "packages", it is meant that they handle the corresponding
introspective representations of those objects by instances of the
classes defined herein: :class:`Module` and :class:`Package`.

.. warning::
    Support for modules defined in shared object libraries is limited.

..
    TODOC: document in what ways support for modules defined in shared
    object libraries is limited, and raise specific exceptions when an
    unsupported request is made

"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__credits__ = ["Ivan D Vasin"]
__docformat__ = "restructuredtext"

import datetime as _datetime
import logging as _logging
import os as _os
import random as _random
import re as _re
import sys as _sys

from . import _exc
from . import _objects as _intro_objects
from . import _paths as _intro_paths


def module_from_filepath(filepath):

    """An introspective representation of the module at some file path.

    If *filepath* is a path to a package directory or :term:`init module`,
    then the result is a :class:`Package`.  If it is a module file path, the
    result is a :class:`Module`.  Otherwise, the result is :obj:`None`.

    :param str filepath:
        A :term:`file path`.

    :rtype: :class:`Module` or null

    """

    package_dirpath = _intro_paths.package_dirpath_from_filepath(filepath)
    if package_dirpath:
        path = _intro_paths.package_path_from_dirpath(package_dirpath)
        return Package(path, package_dirpath)

    path = _intro_paths.module_path_from_filepath(filepath)
    if path:
        return Module(path, filepath)

    return None


def module_from_object(object):
    """
    Convert a generic introspective representation of a module to a module-
    specific representation.

    If the *object* represents a package, the result is a :class:`Package`.
    If it represents a module, the result is a :class:`Module`.  Otherwise,
    the result is :obj:`None`.

    If specified by the *object*, this respects the
    :attr:`Object.load_tree_filepath
    <spruce.introspect._objects.Object.load_tree_filepath>` and
    :attr:`Object.load_fallback_outoftree
    <spruce.introspect._objects.Object.load_fallback_outoftree>`
    settings.

    :param object:
        An object.
    :type object: :class:`~spruce.introspect._objects.Object`

    :rtype: :class:`Module`

    """
    if '__file__' in object.attrnames:
        return module_from_filepath(object.pyattr('__file__'))
    else:
        if '__name__' in object.attrnames:
            module_path = object.pyattr('__name__')
        else:
            module_path = object.path
        if object.load_tree_filepath:
            return module_from_path_intree(module_path,
                                           object.load_tree_filepath,
                                           fallback_outoftree=
                                               object.load_fallback_outoftree)
        else:
            return module_from_path(module_path)


def module_from_path(path):
    """An introspective representation of the module at some module path.

    If the specified module is not found, the result is :obj:`None`.

    :param str path:
        A :term:`module path`.

    :rtype: :class:`Module` or null

    """
    filepath = _intro_paths.module_path_to_filepath(path, package_dirpath=True)
    if filepath:
        if _os.path.isdir(filepath):
            return Package(path, filepath)
        else:
            return Module(path, filepath)
    else:
        return None


def module_from_path_intree(path, tree_filepath, fallback_outoftree=False):
    """
    An introspective representation of a module at some module path in a
    particular module hierarchy.

    If the specified module is not found, the result is :obj:`None`.

    :param str path:
        A :term:`module path`.

    :param str tree_filepath:
        A :term:`file path` within a module hierarchy.

    :param bool fallback_outoftree:
        Whether to fall back to searching in :attr:`sys.path` if the
        specified module is not found in the specified module hierarchy.

    :rtype: :class:`Module` or null

    """
    filepath = \
        _intro_paths.module_path_to_filepath_intree(path, tree_filepath,
                                                   package_dirpath=True)
    if filepath:
        if _os.path.isdir(filepath):
            return Package(path, filepath)
        else:
            return Module(path, filepath)
    elif fallback_outoftree:
        return module_from_path(path)
    else:
        return None


def module_from_pymodule(pymodule):
    """An introspective representation of a Python module object.

    This inspects :samp:`{pymodule}.__file__` and returns a corresponding
    :class:`Module`.

      * If there is no :attr:`!__file__`---for example, if *pymodule* is a
        built-in module such as :mod:`sys`---then the result is a
        :class:`Module` with no :attr:`~Module.filepath`.

      * If the :attr:`!__file__` is an :term`init module`, then the result
        is a :class:`Package`.

      * Otherwise, the result is a normal :class:`Module`.

    :param module pymodule:
        A Python module.

    :rtype: :class:`Module`

    """
    path = pymodule.__name__
    if not hasattr(pymodule, '__file__'):
        return Module(path, None)
    filepath = pymodule.__file__
    if _intro_paths.filepath_identifies_package(filepath):
        return Package(path, filepath)
    else:
        return Module(path, filepath)


def module_path_isstandard(path):
    """Whether a particular module path is part of the standard library.

    :param str path:
        A :term:`module path`.

    :rtype: :obj:`bool`

    """
    if path in _sys.builtin_module_names:
        return True
    module = module_from_path(path)
    if module:
        return module.isstandard
    else:
        return False


def module_path_toabs(path, currentmodule):

    """Convert a module path to an absolute module path.

    If *path* is already absolute, it is returned unchanged.  If *path* is
    relative, it is resolved relative to *currentmodule*.

    :param str path:
        A :term:`module path`.

    :param currentmodule:
        The module in which the path is used.
    :type currentmodule: :class:`Module`

    :rtype: :obj:`str`

    :raise spruce.introspect.InconsistentStructure:
        Raised if *path* is relative but *currentmodule* is not a package
        and has no parent package.

    """

    def raise_invalidpath():
        raise _exc.InvalidRelativeModulePath(path, currentmodule=currentmodule)

    # if necessary, determine the base package for resolving a relative path
    if currentmodule.ispackage:
        base_package = currentmodule
    else:
        base_package = currentmodule.parentmodule
    if not base_package and path.startswith('.'):
        raise_invalidpath()

    # convert implicit relative path to explicit relative path
    if (not path.startswith('.')
        and path.split('.')[0]
            in base_package.submodule_names(include_packages=True,
                                            include_private=True)):
        path = '.' + path

    # convert explicit relative path to absolute path
    if path.startswith('.'):
        if len(path) == 0:
            pass
        elif len(path) == 1:
            path = base_package.path
        else:
            path_rest = path[1:]
            if path_rest.startswith('.'):
                parentmodule = base_package.parentmodule
                if not parentmodule:
                    raise_invalidpath()
                try:
                    path_rest = module_path_toabs(path_rest,
                                                  currentmodule=parentmodule)
                except _exc.InvalidRelativeModulePath:
                    raise_invalidpath()
            path = '{}.{}'.format(base_package.path, path_rest)

    return path


def top_modules(dirpath, include_init=True, include_packages=False,
                include_private=False, excluded_names=None):
    """The modules at the top level of some directory.

    Exclusions are applied after inclusions.

    :param str dirpath:
        A :term:`directory path`.

    :param bool include_init:
        Whether to include the :term:`init module`, if one exists.

    :param bool include_packages:
        Whether to include packages.

    :param bool include_private:
        Whether to include private modules besides the :term:`init module`.

    :param excluded_names:
        Module names that that should be excluded.
    :type excluded_names: [:obj:`str`] or null

    :rtype: [:class:`Module`]

    """
    modules = []
    for name in _intro_paths.top_module_names(dirpath,
                                             include_init=include_init,
                                             include_packages=False,
                                             include_private=include_private,
                                             excluded_names=excluded_names):
        filename = _intro_paths.module_filename_indir(name, dirpath)
        filepath = _os.path.join(dirpath, filename)
        path = _intro_paths.module_path_from_filepath(filepath)
        module = Module(path, filepath)
        modules.append(module)
    if include_packages:
        modules += top_packages(dirpath, include_private=include_private)
    return modules


def top_packages(dirpath, include_private=False, excluded_names=None):
    """The packages at the top level of some directory.

    Exclusions are applied after inclusions.

    :param str dirpath:
        A :term:`directory path`.

    :param bool include_private:
        Whether to include private packages.

    :param excluded_names:
        Package names that that should be excluded.
    :type excluded_names: [:obj:`str`] or null

    :rtype: [:class:`Package`]

    """
    packages = []
    for name in _intro_paths.top_package_names(dirpath,
                                              excluded_names=excluded_names):
        package_dirpath = _os.path.join(dirpath, name)
        path = _intro_paths.package_path_from_dirpath(package_dirpath)
        package = Package(path, package_dirpath)
        packages.append(package)
    return packages


class Module(_intro_objects.Object):

    """An introspective representation of a Python module.

    :param str path:
        The module's :term:`path <module path>`.

    :param filepath:
        The module's :term:`file path`.  :obj:`None` indicates that the
        module is built into the Python interpreter.
    :type filepath: :obj:`str` or null

    :raise ValueError:
        Raised if neither *path* nor *filepath* identify an importable
        module.

    """

    def __init__(self, path, filepath):

        if not _intro_paths.filepath_identifies_module(filepath):
            raise ValueError('invalid module file path "{}"'.format(filepath))

        self._filepath = _os.path.abspath(filepath)
        parentmodule_path, _, relpath = path.rpartition('.')
        super(Module, self).__init__(parentmodule_path, relpath, filepath)

        if self.metatype is not _intro_objects.Metatype.MODULE:
            raise ValueError('cannot find module at "{}"'.format(path))

    def __eq__(self, other):
        if not isinstance(other, Module):
            return False
        return self.path == other.path

    def __repr__(self):
        return 'Module({}, {})'.format(self.path, self.filepath)

    def __str__(self):
        return self.path

    @property
    def filepath(self):
        """This module's :term:`file path`.

        :type: :obj:`str`

        """
        return self._filepath

    @property
    def included_modules(self):
        """The modules :term:`included <included module>` by this module.

        :type: ~[:class:`Module`]

        :raise spruce.introspect.InconsistentStructure:
            Raised if any of the included modules is imported using a relative
            import, but this module is not a package and is not contained in
            one.
        :raise IOError:
            Raised if the ``.py`` file for this module cannot be read.

        """
        for path in self.included_modules_paths(toabs=True):
            yield self.module_intree(path)

    def included_modules_paths(self, toabs=False):

        """
        The :term:`paths <module path>` of the modules :term:`included
        <included module>` by this module.

        In order for this to work, there must be a ``.py`` file for this module
        in the same directory as this module's file.  If *toabs* is true, then
        the following additional conditions must be met:

            * If any of this module's included modules is imported using a
              relative import, then either this module must be a package or it
              must be contained in one.

            * If this module is a package, it must be importable.  Otherwise,
              this module's parent package must be importable.

        :param bool toabs:
            Whether the paths should be converted to absolute paths.

        :rtype: [:obj:`str`]

        :raise spruce.introspect.InconsistentStructure:
            Raised if any of the included modules is imported using a relative
            import, but this module is not a package and is not contained in
            one.
        :raise IOError:
            Raised if the ``.py`` file for this module cannot be read.

        """

        # FIXME: generalize the source code analysis part to provide
        #     information on all imports, and move it to :mod:`.sourcecode`

        paths = []
        included_module_pattern = \
            r'^\s*from[\s\n\\]*([\w\.]+)[\s\n\\]*import[\s\n\\]*\*'
        included_module_re = _re.compile(included_module_pattern,
                                         _re.DOTALL | _re.MULTILINE)
        if self.filepath.endswith('.py'):
            py_filepath = self.filepath
        elif self.filepath.endswith('.so'):
            py_filepath = self.filepath[:-3] + '.py'
        else:
            py_filepath = self.filepath[:-1]
        if not py_filepath.endswith('.py'):
            raise RuntimeError('invalid module file name "{}"'
                                   .format(self.filepath))

        for line in open(py_filepath):
            statements = line.split(';')
            for statement in statements:
                match = _re.match(included_module_re, statement)
                if match:
                    paths.append(match.group(1))

        if toabs:
            for i, path in enumerate(paths):
                paths[i] = module_path_toabs(path, currentmodule=self)

        return paths

    @property
    def ispackage(self):
        """Whether this module is a package.

        :type: :obj:`bool`

        """
        return False

    @property
    def isstandard(self):
        """Whether this module is part of the standard library.

        :type: :obj:`bool`

        """
        if self.path in _sys.builtin_module_names:
            return True
        else:
            def rootmodule():
                module = self
                parent = module.parentmodule
                while parent:
                    module = parent
                    parent = module.parentmodule
                return module
            rootmodule_dirpath = _os.path.dirname(rootmodule().filepath)
            datetime_dirpath = _os.path.dirname(_datetime.__file__)
            logging_dirpath = _os.path.dirname(_logging.__file__)
            os_dirpath = _os.path.dirname(_os.__file__)
            random_dirpath = _os.path.dirname(_random.__file__)
            if rootmodule_dirpath in [datetime_dirpath, logging_dirpath,
                                      os_dirpath, random_dirpath]:
                return True
        return False

    def module_intree(self, path, fallback_outoftree=False):
        """A module in this module's hierarchy.

        :param str path:
            A :term:`module path`.

        :param bool fallback_outoftree:
            Whether to fall back to searching in :attr:`sys.path` if the
            specified module is not found in this module's hierarchy.

        :rtype: :class:`Module`

        """
        return module_from_path_intree(path, self.filepath,
                                       fallback_outoftree=fallback_outoftree)

    @property
    def parentmodule(self):
        """This module's parent package.

        If this module has a parent package, this is it.  Otherwise, this is
        :obj:`None`.

        :type: :class:`Package` or null

        """
        if self.parentmodule_path:
            return self.module_intree(self.parentmodule_path,
                                      fallback_outoftree=False)
        else:
            return None

    @property
    def _ismodule(self):
        return True


class Package(Module):

    """An introspective representation of a Python package.

    A package has a dual identity in a file system.  Like other modules, a
    Python source or bytecode file declares its existence and populates its
    namespace.  For a package, this file in called the :term:`init module`.
    But unlike other modules, it can also contain modules that can be
    imported and then referenced as descendants of it.  In this sense, the
    package is identified with the directory that contains its init module.
    A :class:`!Package` object treats its init module's :term:`file path` as
    its file path and the containing :term:`directory's path <directory
    path>` as its directory path.  Its name is its :term:`directory name`.

    :param str filepath:
        The package's :term:`file path` or :term:`directory path`.

    :raise ValueError:
        Raised if:

          * *filepath* does not refer to an existing file or

          * *filepath* is a directory that does not contain an init module.

    """

    def __init__(self, path, filepath):

        if not _intro_paths.filepath_identifies_package(filepath):
            raise ValueError('invalid package file path "{}"'.format(filepath))

        if _os.path.isdir(filepath):
            filepath = _intro_paths.initmodule_filepath_indir(filepath)
        super(Package, self).__init__(path, filepath)

    def __repr__(self):
        return 'Package({}, {})'.format(self.path, self.dirpath)

    def __str__(self):
        return self.path

    @property
    def dirpath(self):
        """This package's :term:`directory path`.

        This is the absolute path of the directory that contains this package's
        modules.

        :type: :obj:`str`

        """
        return _os.path.dirname(self.filepath)

    @property
    def ispackage(self):
        """

        .. seealso:: :attr:`Module.ispackage`

        """
        return True

    def submodule_names(self, include_init=False, include_packages=False,
                        include_private=False, excluded_names=None):
        """The :term:`names <module name>` of the modules in this package.

        .. seealso:: :func:`~spruce.introspect._paths.top_module_names`.

        :rtype: [:obj:`str`]

        """
        return _intro_paths.top_module_names(self.dirpath,
                                             include_init=include_init,
                                             include_packages=include_packages,
                                             include_private=include_private,
                                             excluded_names=excluded_names)

    def submodules(self, include_init=False, include_packages=False,
                   include_private=False, excluded_names=None):
        """The modules in this package.

        This is a convenience wrapper for :func:`top_modules`.

        :param bool include_init:
            Whether to include the :term:`init module`, if one exists.

        :param bool include_packages:
            Whether to include packages.

        :param bool include_private:
            Whether to include private modules besides the :term:`init module`.

        :param excluded_names:
            Module names that that should be excluded.
        :type excluded_names: [:obj:`str`] or null

        :rtype: [:class:`~spruce.introspect._modules.Module`]

        """
        return top_modules(self.dirpath, include_init=include_init,
                           include_packages=include_packages,
                           include_private=include_private,
                           excluded_names=excluded_names)

    def subpackage_names(self, include_private=False, excluded_names=None):
        """The names of the packages at the top level of some directory.

        This is a convenience wrapper for :func:`top_package_names()
        <spruce.introspect._path.top_package_names>`.

        :param bool include_private:
            Whether to include private packages.

        :param excluded_names:
            Package names that that should be excluded.
        :type excluded_names: [:obj:`str`] or null

        :rtype: [:obj:`str`]

        """
        return _intro_paths.top_package_names(self.dirpath,
                                              include_private=include_private,
                                              excluded_names=excluded_names)

    def subpackages(self, include_private=False, excluded_names=None):
        """The packages at the top level of some directory.

        This is a convenience wrapper for :func:`top_packages`.

        :param bool include_private:
            Whether to include private packages.

        :param excluded_names:
            Package names that that should be excluded.
        :type excluded_names: [:obj:`str`] or null

        :rtype: [:class:`Package`]

        """
        return top_packages(self.dirpath, include_private=include_private,
                            excluded_names=excluded_names)
