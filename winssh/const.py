"""

(c) 2023 by Bas ten Berge. All rights reserved

This program is distributed in the hope that it will be useful, but is provided AS IS with ABSOLUTELY NO WARRANTY;
The entire risk as to the quality and performance of the program is with you. Should the program prove defective,
you assume the cost of all necessary servicing, repair or correction. In no event will any of the developers, or
any other party, be liable to anyone for damages arising out of the use or inability to use the program.
You may copy and distribute copies of the Program, provided that you keep intact all the notices that refer to the
absence of any warranty.

"""
_GRID_PAD = 8
GRID_PADX = _GRID_PAD
GRID_PADY = _GRID_PAD
GRID_STICKY_MODE = 'nsew'

GROUP_ALL = '__all__'
GROUP_LABEL_FOR_ALL = 'Show all'
SECTION_GLOBAL = 'DEFAULT'

# Probably Windows specific, but hey...
OPENSSH_CODE_INACTIVE_SERVICE = 2
OPENSSH_DIR = 'C:/Windows/System32/OpenSSH'


__all__ = [
    'GRID_PADX',
    'GRID_PADY',
    'GRID_STICKY_MODE',
    'GROUP_ALL',
    'GROUP_LABEL_FOR_ALL',
    'OPENSSH_CODE_INACTIVE_SERVICE',
    'OPENSSH_DIR',
    'SECTION_GLOBAL',
]