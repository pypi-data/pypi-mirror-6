"""Pretty printers.

These are extensions of :class:`pprint.PrettyPrinter`.

"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from pprint import PrettyPrinter as _PrettyPrinter


class CleanStrPrettyPrinter(_PrettyPrinter):
    """A pretty printer that omits quotes around strings."""
    def format(self, object, context, maxlevels, level):
        # TODO: (Python 3) use ``super(PrettyPrinter, self)`` instead of
        #     ``pprint.PrettyPrinter``
        string, readable, recursive = \
            _PrettyPrinter.format(self, object, context, maxlevels, level)
        if isinstance(object, str) or isinstance(object, unicode):
            string = object
            readable = False
        return string, readable, recursive
