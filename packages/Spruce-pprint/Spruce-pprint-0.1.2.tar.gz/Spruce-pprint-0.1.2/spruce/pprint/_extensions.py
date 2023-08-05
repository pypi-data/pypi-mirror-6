"""Extensions of the standard :mod:`pprint` functions.

The standard :mod:`pprint` functions are:

    * :func:`pprint.pformat`

    * :func:`pprint.pprint`

    * :func:`pprint.isreadable`

    * :func:`pprint.isrecursive`

    * :func:`pprint.saferepr`

"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from . import _pprinters


def pformat_cleanstr(object):
    """
    Pretty-format an object's string representation, omitting quotes around
    strings.

    :param object object:
        An object.

    :rtype: :obj:`str`

    """
    return _CLEAN_STR_PRETTY_PRINTER.pformat(object)


def pprint_cleanstr(object):
    """
    Pretty-print an object's string representation, omitting quotes around
    strings.

    :param object object:
        An object.

    """
    _CLEAN_STR_PRETTY_PRINTER.pprint(object)


_CLEAN_STR_PRETTY_PRINTER = _pprinters.CleanStrPrettyPrinter()
