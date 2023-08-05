"""Exceptions."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__credits__ = ["Ivan D Vasin"]
__docformat__ = "restructuredtext"


class InconsistentStructure(RuntimeError):
    """An introspected object's structure was found to be inconsistent.

    :param object object:
        An object or a representation thereof.

    :param str message:
        A description of the inconsistency detected in the *object*\ 's
        structure.

    """
    def __init__(self, object, message):
        super(InconsistentStructure, self)\
         .__init__('inconsistent structure in {}: {}'.format(object, message))


class InvalidObject(RuntimeError):
    """An introspected object is invalid.

    :param str object_path:
        An :term:`object path`.

    :param str message:
        A description of the invalidity detected in the specified object.

    """
    def __init__(self, object_path, message=None):
        super_message = 'invalid object {}'.format(object_path)
        if message:
            super_message += ': {}'.format(message)
        super(InvalidObject, self).__init__(super_message)


class InvalidRelativeModulePath(InconsistentStructure):
    """An invalid relative module path was found in some module.

    :param str path:
        A relative :term:`module path`.

    :param object currentmodule:
        A module or a representation thereof.

    """
    def __init__(self, path, currentmodule):
        super(InvalidRelativeModulePath, self)\
         .__init__(currentmodule,
                   'invalid relative module path {}'.format(path))
