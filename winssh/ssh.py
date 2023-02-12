"""

(c) 2023 by Bas ten Berge. All rights reserved

This program is distributed in the hope that it will be useful, but is provided AS IS with ABSOLUTELY NO WARRANTY;
The entire risk as to the quality and performance of the program is with you. Should the program prove defective,
you assume the cost of all necessary servicing, repair or correction. In no event will any of the developers, or
any other party, be liable to anyone for damages arising out of the use or inability to use the program.
You may copy and distribute copies of the Program, provided that you keep intact all the notices that refer to the
absence of any warranty.

"""
from subprocess import CREATE_NEW_CONSOLE, run


def start_ssh_session(*args):
    """
    Starts a new SSH session. This is intended to be run within the processing API as it needs to detach from this app when running
    on Windows
    
    """
    run(
        args,
        creationflags=CREATE_NEW_CONSOLE,
    )


__all__ = [
    'start_ssh_session',
]