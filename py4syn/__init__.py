import collections

global mtrDB
mtrDB = {}

global counterDB
counterDB = collections.OrderedDict()

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
