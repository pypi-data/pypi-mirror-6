"""
This module provides utilities or wraps existing modules/packages into
tools universal across supported Python versions.
"""



import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from collections import OrderedDict
except ImportError:
    from monolith.utils.ordereddict import OrderedDict

try:
    str = str
except NameError:
    str = str = str

if sys.version_info < (2, 7):
    from contextlib import nested
else:
    def nested(*context_managers):
        return tuple(context_managers)


__all__ = ['unittest', 'OrderedDict', 'nested', 'unicode']

