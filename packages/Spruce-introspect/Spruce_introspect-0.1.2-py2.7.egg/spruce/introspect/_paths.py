"""Tools for searching, manipulating, and converting paths.

Many of these functions together provide a translation layer from
:term:`file <file path>` and :term:`directory paths <directory path>` to
:term:`module <module path>` and :term:`package paths <package path>`.

"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__credits__ = ["Ivan D Vasin"]
__docformat__ = "restructuredtext"

from functools import wraps as _wraps
import os as _os
import re as _re
import sys as _sys


def filepath_identifies_module(filepath):
    """Whether a particular file path identifies a module file.

    :param str filepath:
        A :term:`file path`.

    :rtype: :func:`bool`

    """
    return module_name_from_filepath(filepath) is not None


def filepath_identifies_package(filepath):
    """
    Whether a particular file path identifies a package directory or init
    module.

    :param str filepath:
        A :term:`file path`.

    :rtype: :func:`bool`

    """
    return package_dirpath_from_filepath(filepath) is not None


def initmodule_filepath_indir(dirpath):
    """A file path to the init module in a particular directory.

    If there is an :term:`init module` in the directory identified by
    *dirpath*, then its file path is returned.  Otherwise, the result is
    :obj:`None`.

    :param str dirpath:
        A :term:`directory path`.

    :rtype: :obj:`str` or null

    """
    for initmodule_filename in _INITMODULE_FILENAMES:
        initmodule_filepath = _os.path.join(dirpath, initmodule_filename)
        if _os.path.isfile(initmodule_filepath):
            return initmodule_filepath
    return None


def module_filename_indir(module_name, dirpath):
    """
    The name of a file that defines a particular module in some directory.

    This is the first file name returned by :func:`module_filenames_indir`.
    If there is no such file, the result is :obj:`None`.

    .. seealso:: :func:`module_filenames_indir`

    :rtype: :obj:`str` or null

    """
    filenames = module_filenames_indir(module_name, dirpath)
    if filenames:
        return filenames[0]
    else:
        return None


def module_filenames_indir(module_name, dirpath):
    """
    The names of the files that define a particular module in some
    directory.

    The file names are ordered as follows:

        #. ``.py`` file

        #. ``.pyc`` file

        #. ``.pyo`` file

        #. ``.pyd`` file

        #. ``.so`` file

    :param str module_name:
        A :term:`module name`.

    :param str dirpath:
        A :term:`directory path`.

    :rtype: [:obj:`str`]

    """
    filenames = []
    for extension in _MODULE_FILE_EXTENSIONS:
        filename = module_name + extension
        filepath = _os.path.join(dirpath, filename)
        if _os.path.isfile(filepath):
            filenames.append(filename)
    return filenames


def module_filetype(filepath):
    """The type of module file that is specified by some file path.

    :rtype: :class:`ModuleFileType`

    """
    for filetype, extensions in ModuleFileType.extensions.items():
        if any(filepath.endswith(extension) for extension in extensions):
            return filetype
    return ModuleFileType.UNKNOWN


def module_name_from_filepath(filepath):
    """The name of the module at a particular file path.

    If *filepath* identifies a Python module file, then the result is the
    :term:`file name` sans :term:`file extension`.  Otherwise, the result is
    :obj:`None`.

    :param str filepath:
        A :term:`file path`.

    :rtype: :obj:`str` or null

    """
    filename = _os.path.basename(filepath)
    match = _re.match(_MODULE_FILENAME_RE, filename)
    if match:
        return match.group(1)
    else:
        return None


def module_path_from_filepath(filepath):
    """The module path of the module at a particular file path.

    If *filepath* identifies a Python module file, then the result is a
    concatenation of :func:`package_path_from_dirpath` and
    :func:`module_name_from_filepath`.  Otherwise, the result is
    :obj:`None`.

    :param str filepath:
        A :term:`file path`.

    :rtype: :obj:`str` or null

    """
    path = module_name_from_filepath(filepath)
    if not path:
        return None
    package_path = package_path_from_dirpath(_os.path.dirname(filepath))
    if package_path:
        path = '{}.{}'.format(package_path, path)
    return path


def module_path_to_filepath(path, package_dirpath=False):
    """A file path for a particular module.

    If successful, the result is a :term:`file path` to the module.
    Otherwise, the result is :obj:`None`.

    :param str path:
        A :term:`module path`.

    :param bool package_dirpath:
        Whether to return a directory path if *path* references a package.
        If false, the result is an :term:`init module` :term:`file
        path`.

    :rtype: :obj:`str` or null

    """
    if '.' in path:
        for searchpath in _sys.path:
            if not _os.path.isdir(searchpath):
                continue
            for package_name in top_package_names(searchpath,
                                                  include_private=True):
                filepath = \
                    module_path_to_filepath_indir(path, searchpath,
                                                  package_dirpath=
                                                      package_dirpath)
                if filepath:
                    return filepath
    else:
        for searchpath in _sys.path:

            if not _os.path.isdir(searchpath):
                continue
            for package_name in top_package_names(searchpath,
                                                  include_private=True):
                if package_name == path:
                    return _os.path.join(searchpath, package_name)
            for module_name in top_module_names(searchpath,
                                                include_init=True,
                                                include_private=True):
                if module_name == path:
                    filename = module_filename_indir(module_name, searchpath)
                    filepath = _os.path.join(searchpath, filename)
                    return filepath
    return None


def module_path_to_filepath_indir(path, dirpath, package_dirpath=False):
    """
    A file path for a particular module in some directory.

    This function searches for a file that defines the given module *path*
    within a directory tree of packages and modules under *dirpath*.
    The given directory is traversed to ascertain the existence of a module
    with the given *path*.  To match, the root of the target module's
    module hierarchy file or subdirectory within the specified directory.
    If successful, the result is a :term:`file path` to the module.
    Otherwise, the result is :obj:`None`.

    :param str path:
        A :term:`module path`.

    :param str dirpath:
        A :term:`directory path`.

    :param bool package_dirpath:
        Whether to return a :term:`directory path` if *path* identifies a
        package.  If false, then the result is an :term:`init module`
        :term:`file path`.

    :rtype: :obj:`str` or null

    """
    if not _os.path.isdir(dirpath):
        return None
    pathparts = path.split('.')
    while pathparts:
        tree_modulenames = top_module_names(dirpath,
                                            include_init=True,
                                            include_packages=True,
                                            include_private=True)
        pathpart = pathparts.pop(0)
        if any(modulename == pathpart for modulename in tree_modulenames):
            dirpath_next = _os.path.join(dirpath, pathpart)
            if _os.path.isdir(dirpath_next):
                if pathparts:
                    # continue searching
                    dirpath = dirpath_next
                else:
                    # maybe found the right package
                    initmodule_filepath = \
                        initmodule_filepath_indir(dirpath_next)
                    if initmodule_filepath:
                        if package_dirpath:
                            return _os.path.dirname(initmodule_filepath)
                        else:
                            return initmodule_filepath
            elif not pathparts:
                # maybe found the right module
                tree_dir_files = _os.listdir(dirpath)
                for filename in [pathpart + extension
                                 for extension
                                 in _MODULE_FILE_EXTENSIONS]:
                    if filename in tree_dir_files:
                        return _os.path.join(dirpath, filename)
            else:
                # hit a dead end (a non-directory file) with some path parts
                #     remaining
                break
    return None


def module_path_to_filepath_intree(path, tree_filepath, package_dirpath=False):
    """
    A file path for a particular module within some module hierarchy.

    This is a convenience function that uses :func:`root_module_filepath`
    and :func:`module_path_to_filepath_indir`.

    .. seealso:: :func:`module_path_to_filepath_indir`

    :param str tree_filepath:
        A :term:`file path` within a module hierarchy.

    :rtype: :obj:`str` or null

    """
    root_filepath = root_module_filepath(tree_filepath)
    if root_filepath:
        dirpath = _os.path.dirname(root_filepath)
        return module_path_to_filepath_indir(path, dirpath,
                                             package_dirpath=package_dirpath)


def package_name_from_dirpath(dirpath):
    """The name of the package that corresponds to a particular directory.

    If *dirpath* identifies a package directory, then the result is that
    package's :term:`name <package name>`.  Otherwise, the result is
    :obj:`None`.

    :param str dirpath:
        A :term:`directory path`.

    :rtype: :obj:`str` or null

    """
    if initmodule_filepath_indir(dirpath):
        return _os.path.basename(dirpath)
    else:
        return None


def package_path_from_dirpath(dirpath):
    """The path of the package that corresponds to a particular directory.

    If *dirpath* identifies a package directory, then the result is that
    package's :term:`path <package path>`.  Otherwise, the result is
    :obj:`None`.

    :param str dirpath:
        A :term:`directory path`.

    :rtype: :obj:`str` or null

    """
    package_path = _package_path_from_dirpath_helper(dirpath)
    if package_path:
        return package_path
    else:
        return None


def package_dirpath_from_filepath(filepath):
    """A directory path to the package identified by a particular file path.

    If *filepath* is a package directory, then the result is the given
    *filepath*.  If *filepath* is a path to an :term`init module`, then
    the result is a path to its containing directory.  If neither is the
    case, the result is :obj:`None`.

    :param str filepath:
        A :term:`directory path` to a package or a :term:`file path` to an
        :term:`init module`.

    :rtype: :obj:`str` or null

    """
    if _os.path.isdir(filepath) and any(filename in _os.listdir(filepath)
                                        for filename in _INITMODULE_FILENAMES):
        return filepath
    elif any(filepath.endswith(filename)
             for filename in _INITMODULE_FILENAMES):
        return _os.path.dirname(filepath)
    else:
        return None


def root_module_filepath(filepath):

    """A file path to the root module for a particular module file path.

    If *filepath* identifies a file or directory that corresponds to the
    highest module in a module hierarchy, then *filepath* is returned.  If
    *filepath* is part of a module hierarchy that originates at a higher
    directory, then the result is a path to that origin.  Otherwise---if
    *filepath* does not identify a module or package---the result is
    :obj:`None`.

    :param str filepath:
        A :term:`file path`.

    :rtype: :obj:`str` or null

    """

    if not (filepath_identifies_module(filepath)
            or filepath_identifies_package(filepath)):
        return None

    if _os.path.isdir(filepath):
        dirpath = filepath
    else:
        dirpath = _os.path.dirname(filepath)
    package_path = package_path_from_dirpath(dirpath)

    if not package_path:
        return filepath

    package_pathparts = package_path.split('.')
    ancestor_filepath = dirpath
    while package_pathparts:
        ancestor_filepath, dirname = _os.path.split(ancestor_filepath)
        pathpart = package_pathparts.pop()
        # if this fails, something is wrong with
        #     :func:`package_path_from_dirpath`
        assert dirname == pathpart, \
               '{} and {} differ'.format(dirname, pathpart)
    return _os.path.join(ancestor_filepath, dirname)


def top_module_names(dirpath, include_init=False, include_packages=False,
                     include_private=False, excluded_names=None):
    """The names of the modules at the top level of some directory.

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

    :rtype: [:obj:`str`]

    :raise OSError:
        Raised if the directory contents of *dirpath* cannot be listed.

    """
    names = set()
    try:
        filenames = _os.listdir(dirpath)
    except OSError as exc:
        raise OSError('reading top modules at {}: {}'.format(dirpath, exc))
    for filename in filenames:
        if not include_init and filename in _INITMODULE_FILENAMES:
            continue
        elif not include_private and filename.startswith('_'):
            continue

        filepath = _os.path.join(dirpath, filename)
        if _os.path.isfile(filepath):
            module_name = module_name_from_filepath(filepath)
            if module_name:
                if excluded_names and module_name in excluded_names:
                    continue

                names.add(module_name)
    if include_packages:
        names |= top_package_names(dirpath, include_private=include_private)
    return names


def top_package_names(dirpath, include_private=False, excluded_names=None):
    """The names of the packages at the top level of some directory.

    Exclusions are applied after inclusions.

    :param str dirpath:
        A :term:`directory path`.

    :param bool include_private:
        Whether to include private packages.

    :param excluded_names:
        Package names that that should be excluded.

    :type excluded_names: [:obj:`str`] or null

    :rtype: [:obj:`str`]

    """
    names = set()
    try:
        filenames = _os.listdir(dirpath)
    except OSError as exc:
        raise OSError('reading top modules at {}: {}'.format(dirpath, exc))
    for filename in filenames:
        if not include_private and filename.startswith('_'):
            continue

        filepath = _os.path.join(dirpath, filename)
        if _os.path.isdir(filepath):
            if initmodule_filepath_indir(filepath):
                if excluded_names and filename in excluded_names:
                    continue

                names.add(filename)
    return names


def _enum(*valid_names):
    def enum_inner(class_):
        instances = {}

        @_wraps(class_, ('name',))
        def instance(name, value):
            if name not in instances:
                if name not in valid_names:
                    raise ValueError('invalid {} instance name "{}"'
                                         .format(class_.__name__, name))
                instances[name] = class_(name, value)
            return instances[name]
        return instance
    return enum_inner

_module_filetype_map = {'UNKNOWN': -1, 'SOURCE': 1, 'COMPILED': 2,
                        'DYNAMIC': 3}

@_enum(*_module_filetype_map.keys())
class ModuleFileType(object):

    """A module file type."""

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def __eq__(self, other):
        return self._value == other._value

    def __repr__(self):
        return '{}.{}'.format(self.__class__.__name__, self.name)

    def __str__(self):
        return self.name.lower()

    COMPILED = None

    DYNAMIC = None

    extensions = None

    @property
    def name(self):
        return self._name

    SOURCE = None

    UNKNOWN = None

def _ModuleFileType_init():
    for name, value in _module_filetype_map.iteritems():
        setattr(ModuleFileType, name, ModuleFileType(name, value))

    ModuleFileType.extensions = {ModuleFileType.SOURCE: ['.py'],
                                 ModuleFileType.COMPILED: ['.pyc', '.pyo'],
                                 ModuleFileType.DYNAMIC: ['.pyd', '.so']}
_ModuleFileType_init()


def _package_path_from_dirpath_helper(dirpath, _acc_path=''):
    package_name = package_name_from_dirpath(dirpath)
    if package_name:
        if _acc_path:
            path = '{}.{}'.format(package_name, _acc_path)
        else:
            path = package_name
        parentdirpath = _os.path.dirname(dirpath)
        if parentdirpath != dirpath:
            return _package_path_from_dirpath_helper(parentdirpath, path)
        else:
            return path
    else:
        return _acc_path


_MODULE_FILE_EXTENSIONS = \
    sum((ModuleFileType.extensions[type_]
         for type_ in (ModuleFileType.SOURCE, ModuleFileType.COMPILED,
                      ModuleFileType.DYNAMIC)),
        [])
_MODULE_FILENAME_RE = \
    _re.compile(r'(.+)({})$'
                 .format('|'.join(extension.replace('.', r'\.')
                                  for extension in _MODULE_FILE_EXTENSIONS)))

_INITMODULE_FILENAMES = ['__init__' + extension
                         for extension in _MODULE_FILE_EXTENSIONS]
