"""Attributes."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__credits__ = ["Ivan D Vasin"]
__docformat__ = "restructuredtext"


def getattr_recursive(object, relpath):
    """Apply :func:`getattr` recursively.

    :param object object:
        An object.

    :param str relpath:
        A relative :term:`object path`.

    :rtype: :obj:`object`

    :raise AttributeError:
        Raised if *relpath* does not identify an attribute or nested
        attribute of *object*.

    """
    pathparts = relpath.split('.')
    while pathparts:
        attrname = pathparts.pop(0)
        try:
            object = getattr(object, attrname)
        except AttributeError:
            raise AttributeError('{} {!r} has no attribute {!r}'
                                  .format(object.__class__.__name__, object,
                                          attrname))
    return object
