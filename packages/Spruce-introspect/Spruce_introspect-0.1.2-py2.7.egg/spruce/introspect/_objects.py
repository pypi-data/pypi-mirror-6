"""Objects and types."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__credits__ = ["Ivan D Vasin"]
__docformat__ = "restructuredtext"

import __builtin__
from functools import wraps as _wraps
from importlib import import_module as _import_module

from spruce.pprint import split_blocks as _split_blocks

from . import _exc
from . import _imp as _intro_imp
from . import _paths as _intro_path


# metatypes -------------------------------------------------------------------


_METATYPE_MAP = {'UNKNOWN': -1, 'OLDSTYLE': 1, 'FUNCTION': 2, 'CLASS': 3,
                 'EXCEPTION': 4, 'MODULE': 5}


# FIXME: replace with :class:`enum.Enum` from :pypi:`enum34`
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


@_enum(*_METATYPE_MAP.keys())
class Metatype(object):

    """An object :term:`metatype`."""

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def __eq__(self, other):
        return self._value == other._value

    def __repr__(self):
        return '{}.{}'.format(self.__class__.__name__, self.name)

    def __str__(self):
        return self.name.lower()

    CLASS = None

    EXCEPTION = None

    FUNCTION = None

    MODULE = None

    @property
    def name(self):
        return self._name

    OLDSTYLE = None

    UNKNOWN = None


def _Metatype_init():
    for name, value in _METATYPE_MAP.iteritems():
        setattr(Metatype, name, Metatype(name, value))


_Metatype_init()


# objects ---------------------------------------------------------------------


def object_name_isprivate(name):
    """Whether an object name is private.

    :param str name:
        An :term:`object name`.

    :rtype: :obj:`bool`

    """
    return name.startswith('_')


class Object(object):

    """An introspective representation of a Python object.

    This class provides generic introspection capabilities that apply to
    most or all Python objects.  For subclasses that provide additional
    functions specific to particular object types, see
    :class:`~spruce.introspect._modules.Module` and
    :class:`~spruce.introspect._modules.Package`.

    Some of this class's methods entail loading the represented object.
    If a *load_tree_filepath* is passed to the constructor, or if
    :attr:`load_tree_filepath` is set prior to any calls to those methods,
    then the load operation will be attempted in the specified package
    hierarchy.  Likewise, *load_fallback_outoftree* and
    :attr:`load_fallback_outoftree` control whether the load operation will
    fall back to loading the object using :attr:`sys.path`.

    :param parentmodule_path:
        The :term:`path <module path>` of the object's :term:`parent
        module`.  If this is null or empty, it is taken to mean that the
        object is a standalone module or the root package of a package
        hierarchy.
    :type parentmodule_path: :obj:`str` or null

    :param str relpath:
        The object's :term:`path <object path>`, relative to the
        *parentmodule_path*.

    :param load_tree_filepath:
        A :term:`file path` within the package hierarchy from which this
        object should be loaded, if necessary.  If no package hierarchy is
        preferred, this should be :obj:`None`.
    :type load_tree_filepath: :obj:`str` or null

    :param bool load_fallback_outoftree:
        Whether a load operation on this object should fall back to loading
        it from :attr:`sys.path`.

    """

    def __init__(self, parentmodule_path, relpath, load_tree_filepath=None,
                 load_fallback_outoftree=True):
        self._imported_self = None
        self._metatype = None
        self._parentmodule_path = parentmodule_path
        self._relpath = relpath
        self.load_fallback_outoftree = load_fallback_outoftree
        self.load_tree_filepath = load_tree_filepath

    def __eq__(self, other):
        if not isinstance(other, Object):
            return False
        return self.parentmodule_path == other.parentmodule_path \
               and self.name == other.name

    def __repr__(self):
        return 'Object({})'.format(self.path)

    def attr(self, name):
        """An attribute of this object.

        :param str name:
            An attribute :term:`name <object name>`.

        :rtype: :class:`Object`

        """
        if self._ismodule:
            parentmodule_path = self.path
            relpath = name
        else:
            parentmodule_path = self.parentmodule_path
            relpath = '{}.{}'.format(self.relpath, name)
        return Object(parentmodule_path, relpath,
                      load_tree_filepath=self.load_tree_filepath)

    @property
    def attrnames(self):
        """The :term:`names <object name>` of this object's attributes.

        :type: [:obj:`str`]

        :raise AttributeError:
            Raised if this object is not defined at the location specified by
            :attr:`parentmodule_path` and :attr:`relpath`.

        :raise ImportError:
            Raised if this object is a module but cannot be imported.

        :raise spruce.introspect.InvalidObject:
            Raised if this object is not a module and has no parent module.

        """
        return dir(self.pyobject())

    @property
    def class_(self):
        """This object's class.

        :type: :obj:`type`

        :raise AttributeError:
            Raised if this object is not defined at the location specified by
            :attr:`parentmodule_path` and :attr:`relpath`.

        :raise ImportError:
            Raised if this object is a module but cannot be imported.

        :raise spruce.introspect.InvalidObject:
            Raised if this object is not a module and has no parent module.

        """
        return self.pyobject().__class__

    @property
    def classname(self):
        """The :term:`name <object name>` of this object's class.

        :type: :obj:`str`

        :raise AttributeError:
            Raised if this object is not defined at the location specified by
            :attr:`parentmodule_path` and :attr:`relpath`.

        :raise ImportError:
            Raised if this object is a module but cannot be imported.

        :raise spruce.introspect.InvalidObject:
            Raised if this object is not a module and has no parent module.

        """
        return self.class_.__name__

    @property
    def docstring(self):
        """This object's docstring.

        If there is no docstring, this is the empty string.

        :type: :obj:`str`

        :raise AttributeError:
            Raised if this object is not defined at the location specified by
            :attr:`parentmodule_path` and :attr:`relpath`.

        :raise ImportError:
            Raised if this object is a module but cannot be imported.

        :raise spruce.introspect.InvalidObject:
            Raised if this object is not a module and has no parent module.

        """
        pyobject = self.pyobject()
        if hasattr(pyobject, '__doc__') and pyobject.__doc__:
            return pyobject.__doc__
        else:
            return ''

    @property
    def isbuiltin(self):
        """Whether this object is built into the Python interpreter.

        :type: :obj:`bool`

        """
        return hasattr(__builtin__, self.path)

    @property
    def isprivate(self):
        """Whether this object is private.

        This is a convenience wrapper for :func:`object_name_isprivate`.

        :type: :obj:`bool`

        """
        return object_name_isprivate(self.name)

    @property
    def load_fallback_outoftree(self):
        """
        Whether a load operation on this object should fall back to loading it
        from :attr:`sys.path`.

        :type: :obj:`bool`

        .. seealso:: :attr:`load_tree_filepath`

        """
        return self._load_fallback_outoftree

    @load_fallback_outoftree.setter
    def load_fallback_outoftree(self, enable):
        self._load_fallback_outoftree = enable

    @property
    def load_tree_filepath(self):
        """
        A :term:`file path` within the package hierarchy from which this
        object should be loaded, if necessary.

        If no package hierarchy is preferred, this is :obj:`None`.

        :type: :obj:`str` or null

        .. seealso:: :attr:`load_fallback_outoftree`

        """
        return self._tree_root_filepath

    @load_tree_filepath.setter
    def load_tree_filepath(self, filepath):
        if filepath is None:
            self._tree_root_filepath = None
        else:
            self._tree_root_filepath = \
                _intro_path.root_module_filepath(filepath)

    @property
    def metatype(self):
        """This object's :term:`metatype`.

        In most cases, this is determined by inspecting this object's
        :meth:`pyobject`.

        :type: :class:`Metatype`

        :raise AttributeError:
            Raised if this object is not defined at the location specified by
            :attr:`parentmodule_path` and :attr:`relpath`.

        :raise ImportError:
            Raised if this object is a module but cannot be imported.

        :raise spruce.introspect.InvalidObject:
            Raised if this object is not a module and has no parent module.

        """
        if self._metatype is None:
            def infer_metatype(pyobject):
                if hasattr(pyobject, '__class__'):
                    if hasattr(pyobject, '__bases__'):
                        if isinstance(pyobject, Exception):
                            return Metatype.EXCEPTION
                        else:
                            return Metatype.CLASS
                    elif hasattr(pyobject, '__package__') \
                         or hasattr(pyobject, '__path__'):
                        return Metatype.MODULE
                    else:
                        classname = pyobject.__class__.__name__
                        if classname == 'function' \
                               or classname == 'instancemethod' \
                               or classname == 'builtin_function_or_method':
                            return Metatype.FUNCTION
                        elif hasattr(pyobject, '__init__') \
                             or hasattr(pyobject, '__subclasshook__'):
                            return Metatype.OLDSTYLE
                        else:
                            return Metatype.UNKNOWN
                else:
                    return Metatype.OLDSTYLE

            if self._ismodule:
                metatype = Metatype.MODULE
            else:
                pyobject = self.pyobject()
                metatype = infer_metatype(pyobject)
            self._metatype = metatype
        return self._metatype

    @property
    def name(self):
        """This object's :term:`name <object name>`.

        :type: :obj:`str`

        """
        _, _, name = self.relpath.rpartition('.')
        return name

    @property
    def parent(self):
        """This object's :term:`parent object`.

        If this object has no parent object, this is :obj:`None`.

        :type: :class:`Object`

        """
        if '.' in self.relpath:
            parentmodule_path = self.parentmodule_path
            relpath, _, _ = self.relpath.rpartition('.')
        elif self.parentmodule_path:
            if '.' in self.parentmodule_path:
                parentmodule_path, _, relpath = \
                    self.parentmodule_path.rpartition('.')
            else:
                parentmodule_path = None
                relpath = self.parentmodule_path
        else:
            return None
        return Object(parentmodule_path, relpath,
                      load_tree_filepath=self.load_tree_filepath)

    @property
    def parentmodule_path(self):
        """
        The :term:`path <module path>` of this object's :term:`parent module`.

        If this object has no parent module, this is :obj:`None`.

        :type: :obj:`str` or null

        """
        return self._parentmodule_path

    @property
    def path(self):
        """This object's :term:`path <object path>`.

        :type: :obj:`str`

        """
        path = ''
        if self.parentmodule_path:
            path += self.parentmodule_path + '.'
        path += self.relpath
        return path

    def pyattr(self, name):
        """An attribute of this object.

        This is the actual Python object that is an attribute of the Python
        object introspected by this object.  For an introspective
        representation of the attribute, use :meth:`attr`.

        :param name:
            An attribute :term:`name <object name>`.
        :type name: :obj:`str`

        :rtype: :obj:`object`

        :raise AttributeError:
            Raised if:

                * this object is not defined at the location specified by
                  :attr:`parentmodule_path` and :attr:`relpath` or

                * this object does not have an attribute with the given
                  *name*.

        :raise ImportError:
            Raised if either this object or the specified attribute is a module
            but cannot be imported.

        :raise spruce.introspect.InvalidObject:
            Raised if this object is not a module and has no parent module.

        """
        return self.attr(name).pyobject()

    def pyobject(self, globals=None, locals=None):
        """The Python object that this object introspects.

        The Python object is retrieved as follows:

          #. If this object corresponds to a built-in Python object, that
             object is returned.

          #. If this object corresponds to one of the given *locals*, that
             object is returned.

          #. If this object corresponds to one of the given *globals*, that
             object is returned.

          #. If this object is a module, it is imported and returned.

          #. Otherwise, if this object has a parent object, the result is
             equivalent to :samp:`getattr({self}.parent.pyobject(),
             {self}.name)`.

        :rtype: :obj:`object`

        :raise AttributeError:
            Raised if this object is not defined at the location specified by
            :attr:`parentmodule_path` and :attr:`relpath`.

        :raise ImportError:
            Raised if this object is a module but cannot be imported.

        :raise spruce.introspect.InvalidObject:
            Raised if this object is not a module and has no parent module.

        .. note:: **TODO:**
            add a means to reload in the cases that rely on imports

        """
        if self.isbuiltin:
            return getattr(__builtin__, self.path)
        elif locals and self.path in locals:
            return locals[self.path]
        elif globals and self.path in globals:
            return globals[self.path]
        elif self._ismodule:
            return self._import_self()
        else:
            parent = self.parent
            if parent:
                return getattr(parent.pyobject(), self.name)
            else:
                raise _exc.InvalidObject(self.path)

    @property
    def relpath(self):
        """
        This object's :term:`path <object path>`, relative to the module
        identified by its :attr:`parentmodule_path`.

        :type: :obj:`str`

        """
        return self._relpath

    @property
    def shortdoc(self):
        """The first block of this module's docstring.

        This is a convenience property that returns the first paragraph of
        :attr:`docstring`.  Typically this is a short phrase.  It is returned
        as one line.

        :type: :obj:`str`

        :raise AttributeError:
            Raised if this object is not defined at the location specified by
            :attr:`parentmodule_path` and :attr:`relpath`.

        :raise ImportError:
            Raised if this object is a module but cannot be imported.

        :raise spruce.introspect.InvalidObject:
            Raised if this object is not a module and has no parent module.

        """
        blocks = _split_blocks(self.docstring)
        if blocks:
            return blocks[0]
        else:
            return ''

    def _import_self(self):
        if self._imported_self is None:
            if self.load_tree_filepath:
                imported_self = \
                    _intro_imp.import_module_intree\
                     (self.path, self.load_tree_filepath,
                      fallback_outoftree=self.load_fallback_outoftree)
            else:
                imported_self = _import_module(self.path)
            self._imported_self = imported_self
        return self._imported_self

    @property
    def _ismodule(self):
        try:
            self._import_self()
        except ImportError:
            return False
        else:
            return True
