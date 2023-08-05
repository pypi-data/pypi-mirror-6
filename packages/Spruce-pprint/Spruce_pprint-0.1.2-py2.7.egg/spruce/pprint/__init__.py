"""String formatting tools.

This is an extension of :mod:`pprint`.

These tools beautify text strings, especially string representations of
Python objects.  They are not responsible for constructing the original
strings or string representations---that is the prerogative of methods
such as :meth:`~object.__repr__` and :meth:`~object.__str__` and of
application-specific formatting functions.

"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__credits__ = ["Ivan D Vasin"]
__maintainer__ = "Ivan D Vasin"
__email__ = "nisavid@gmail.com"
__docformat__ = "restructuredtext"

from ._extensions import *
from ._misc import *
from ._pprinters import *
