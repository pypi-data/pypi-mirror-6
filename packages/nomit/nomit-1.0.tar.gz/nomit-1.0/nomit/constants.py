"""
Contants mirrored from ```monit.h```.

"""

__author__ = "Markus Juenemann <markus@juenemann.net"
__copyright__ = "Copyright (c) 2014 Markus Juenemann"
__license__ = "Simplified BSD License" 
__version__ = "1.0"
__vcs_id__ = "$Id:"


# <service> types
#
TYPE_FILESYSTEM = 0
"""<service><type>0</type></service>"""
TYPE_DIRECTORY = 1
"""<service><type>1</type></service>"""
TYPE_FILE = 2
"""<service><type>2</type></service>"""
TYPE_PROCESS = 3
"""<service><type>3</type></service>"""
TYPE_HOST = 4
"""<service><type>4</type></service>"""
TYPE_SYSTEM = 5
"""<service><type>5</type></service>"""
TYPE_FIFO = 6
"""<service><type>6</type></service>"""
TYPE_PROGRAM = 7
"""<service><type>7</type></service>"""


MONITOR_NOT = 0
"""<service><monitor>0</monitor></service>"""
MONITOR_YES = 1
"""<service><monitor>1</monitor></service>"""
MONITOR_INIT = 2
"""<service><monitor>2</monitor></service>"""
MONITOR_WAITING = 4
"""<service><monitor>4</monitor></service>"""


EVERY_CYCLE = 0
"""<service><every><type>0</type></every></service"""
EVERY_SKIPCYCLES = 1
"""<service><every><type>1</type></every></service"""
EVERY_CRON = 2
"""<service><every><type>2</type></every></service"""
EVERY_NOTINCRON = 3
"""<service><every><type>3</type></every></service"""


STATE_SUCCEEDED = 0
STATE_FAILED = 1
STATE_CHANGED = 2
STATE_CHANGEDNOT = 3
STATE_INIT = 4


ACTION_IGNORE = 0
ACTION_ALERT = 1
ACTION_RESTART = 2
ACTION_STOP = 3
ACTION_EXEC = 4
ACTION_UNMONITOR = 5
ACTION_START = 6
ACTION_MONITOR = 7
