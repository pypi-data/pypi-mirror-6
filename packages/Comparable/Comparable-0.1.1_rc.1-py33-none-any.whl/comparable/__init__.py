#!/usr/bin/env python

"""Package for Comparable."""

__project__ = 'Comparable'
__version__ = '0.1.1-rc.1'

VERSION = __project__ + '-' + __version__

from comparable.base import SimpleComparable, CompoundComparable
from comparable import simple
from comparable import compound
from comparable import tools
