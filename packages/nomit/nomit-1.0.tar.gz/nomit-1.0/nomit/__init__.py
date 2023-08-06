"""
Top-level module of the nomit package.

This module simple makes all other modules available under
the ``nomit`` namespace.

"""

__author__ = "Markus Juenemann <markus@juenemann.net"
__copyright__ = "Copyright (c) 2014 Markus Juenemann"
__license__ = "Simplified BSD License" 
__version__ = "1.0"
__vcs_id__ = "$Id:"

# Load other modules into this namespace
#
from handler import MonitBaseHandler 
from constants import *

