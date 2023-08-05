"""Importing tools."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__credits__ = ["Ivan D Vasin"]
__docformat__ = "restructuredtext"

import imp as _imp
from importlib import import_module as _import_module
import os as _os

from . import _attrs as _intro_attrs
from . import _paths as _intro_paths


def from_module_import_attrs(path, attr_relpaths):
    """Import some attributes of the module at a particular path.

    This imports the module at the given *path* before retrieving the
    attributes with the given *attrnames*.  If any of the names' references
    are modified at import time, then the resulting attributes are the
    objects that are assigned last.

    :param str path:
        An absolute :term:`module path`.

    :param attr_relpaths:
        Relative paths from *path* to some attributes that are available
        after importing *path*.
    :type attr_relpaths: [:obj:`str`]

    :rtype: [:obj:`object`]

    :raise AttributeError:
        Raised if any of the *attr_relpaths* cannot be dereferenced.

    :raise ImportError:
        Raised if *path* cannot be imported.

    """
    imported = __import__(path, fromlist=attr_relpaths, level=0)
    return [_intro_attrs.getattr_recursive(imported, relpath)
            for relpath in attr_relpaths]


def import_module_indir(path, dirpath, fallback_outoftree=False):
    """Import a module at some module path in some directory.

    :param str path:
        A :term:`module path`.

    :param str dirpath:
        A :term:`directory path`.

    :param bool fallback_outoftree:
        Whether to fall back to searching in :obj:`sys.path` if the
        specified module is not found in the specified module hierarchy.

    :rtype: module

    :raise ImportError:
        Raised if the given *path* cannot be imported.

    """
    try:
        return _import_module_indir_helper(path, _os.path.abspath(dirpath))
    except ImportError:
        if fallback_outoftree:
            try:
                return _import_module(path)
            except ImportError as exc:
                raise ImportError('cannot import {}: {}'.format(path, exc))
        else:
            raise ImportError('cannot import {} in directory "{}"'
                               .format(path, dirpath))


def import_module_intree(path, tree_filepath, fallback_outoftree=False):
    """Import a module at a particular module path in some module hierarchy.

    :param str path:
        A :term:`module path`.

    :param str tree_filepath:
        A :term:`file path` within a module hierarchy.

    :param bool fallback_outoftree:
        Whether to fall back to searching in :obj:`sys.path` if the
        specified module is not found in the specified module hierarchy.

    :rtype: module

    :raise ImportError:
        Raised if the given *path* cannot be imported.

    """
    root_filepath = _intro_paths.root_module_filepath(tree_filepath)
    if root_filepath:
        dirpath = _os.path.dirname(root_filepath)
        return import_module_indir(path, dirpath,
                                   fallback_outoftree=fallback_outoftree)
    else:
        raise ImportError('cannot import {} in the module hierarchy at "{}"'
                           .format(path, tree_filepath))


def _import_module_indir_helper(path, dirpath):
    filepath = _intro_paths.module_path_to_filepath_indir(path, dirpath)
    if filepath:
        if '.' in path:
            parentpath, _, _ = path.rpartition('.')
            _import_module_indir_helper(parentpath, dirpath)
        filetype = _intro_paths.module_filetype(filepath)
        if filetype == _intro_paths.ModuleFileType.SOURCE:
            return _imp.load_source(path, filepath)
        elif filetype == _intro_paths.ModuleFileType.COMPILED:
            return _imp.load_compiled(path, filepath)
        elif filetype == _intro_paths.ModuleFileType.DYNAMIC:
            return _imp.load_dynamic(path, filepath)
        else:
            raise RuntimeError('unknown module file type for file "{}"'
                                .format(filepath))
    else:
        raise ImportError(path)
