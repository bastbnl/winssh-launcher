"""

(c) 2023 by Bas ten Berge. All rights reserved

This program is distributed in the hope that it will be useful, but is provided AS IS with ABSOLUTELY NO WARRANTY;
The entire risk as to the quality and performance of the program is with you. Should the program prove defective,
you assume the cost of all necessary servicing, repair or correction. In no event will any of the developers, or
any other party, be liable to anyone for damages arising out of the use or inability to use the program.
You may copy and distribute copies of the Program, provided that you keep intact all the notices that refer to the
absence of any warranty.

"""
from configparser import ConfigParser
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from subprocess import CREATE_NO_WINDOW, CalledProcessError, check_call

from .const import GROUP_ALL as _GROUP_ALL, \
    GROUP_LABEL_FOR_ALL as _GROUP_LABEL_FOR_ALL, \
    OPENSSH_CODE_INACTIVE_SERVICE as _OPENSSH_CODE_INACTIVE_SERVICE, \
    OPENSSH_DIR as _OPENSSH_DIR, \
    SECTION_GLOBAL as _SECTION_GLOBAL


@dataclass(frozen=True, )
class SSHConnectionString:
    label: str
    host: str 
    port: int
    user: str
    group: str=None
    connection_label: str=None

    def __str__(self):
        return self.label


class NativeSSHLauncherConfiguration(
    ConfigParser,
):
    """
    Loads the NativeSSH configuration

    """
    def __init__(self, *args, **kwargs):
        super().__init__(
            converters={
                'list': lambda x: [ee.strip() for ee in filter(lambda e: e.strip(), x.split(','))],
            },
        )
        fallback_to_home_dir = False
        filename = kwargs.get('configfile')
        if filename is None:
            exe_as_path = Path(__file__, )
            filename = Path(
                exe_as_path.parents[0],
                f'{exe_as_path.stem}.ini',
            )
            fallback_to_home_dir = not filename.is_file()
            filename = 'winssh-launcher.ini'
        else:
            fallback_to_home_dir = not Path(filename).is_file()

        if fallback_to_home_dir:
            filename = Path(f'~/.winssh/{filename}').expanduser()

        self.read(filename, )
    
    def _ensure_full_path(self, key_in_section, default_value, **kwargs):
        """
        Returns the full path, including the installdir when needed
        
        """
        to_return = self[_SECTION_GLOBAL].get(key_in_section, )
        if to_return is None:
            to_return = default_value
        
        to_return_as_path = Path(to_return, )
        if not to_return_as_path.is_file():
            to_return_as_path = Path(
                self.ssh_installdir,
                to_return_as_path
            )
            if not to_return_as_path.is_file():
                to_return_as_path = None
        
        if to_return_as_path:
            return to_return_as_path.absolute()
   
    @cached_property
    def ssh_installdir(self):
        """
        Returns the OpenSSH installdir

        """
        to_return = self[_SECTION_GLOBAL].get('ssh.installdir', )
        
        if to_return is None:
            return _OPENSSH_DIR
        
        return to_return

    @cached_property
    def title(self):
        """
        Gets the title for the app 

        """
        to_return = self[_SECTION_GLOBAL].get('app.title', )
        
        if to_return is None:
            to_return = 'WinSSH Launcher'
        
        return to_return
    
    @cached_property
    def ssh_keys(self):
        """
        Gets the absolute paths to the ssh keys 

        """
        to_return = {}
        key_install_path = self[_SECTION_GLOBAL].get('ssh.key.installdir', )
        listed_keys = self[_SECTION_GLOBAL].getlist('ssh.key.pem.filenames', )

        if listed_keys:
            pems = []
            for single_listed_key in listed_keys:
                # Check if `single_listed_key` contains an absolute path
                single_listed_key_path = Path(single_listed_key, )
                if not single_listed_key_path.is_file():
                    single_listed_key_path = Path(
                        key_install_path,
                        single_listed_key,
                    )
                
                if single_listed_key_path not in to_return:
                    if single_listed_key_path.is_file():
                        pems.append(single_listed_key_path)
                    else:
                        # Skip this file as it's not there yet 
                        continue
            
            to_return['pem'] = pems
        
        # TODO: Add pkcs11 keys
        
        return to_return

    @property
    def has_usable_ssh_keys(self):
        """
        Indicates that the configuration contains keys and that the environment has been setup correctly. 
        This fixes the case where the SSH client service is not active on Windows 

        """
        to_return = self.has_ssh_keys
        if to_return:
            # We have keys, but do we have the OpenSSH Authentication Agent service active?
            if self.ssh_add_filename is not None:
                try:
                    check_call(
                        [
                            self.ssh_add_filename,
                            '-l',
                        ],
                        creationflags=CREATE_NO_WINDOW,
                    )
                except CalledProcessError as e:
                    # This probably means the service needs to be started
                    if _OPENSSH_CODE_INACTIVE_SERVICE == e.returncode:
                        to_return = False
        
        return to_return

    @cached_property
    def has_ssh_keys(self):
        """
        Indicates that the configuration contains keys
        
        """
        return bool(self.ssh_keys.values())

    @cached_property
    def ssh_sessions(self, ):
        """
        Loads the SSH sessions 

        """
        to_return = []

        if self.ssh_filename is not None:
            # Each of the sections that are not named global
            for single_section_key in self.sections():
                ssh_host = self[single_section_key].get('host', )
                if ssh_host is None:
                    ssh_host = single_section_key

                ssh_port = self[single_section_key].getint('port', )
                if ssh_port is None:
                    ssh_port = 22 

                ssh_user = self[single_section_key].get('user', )
                connection_label = ssh_host
                if not '@' in connection_label and ssh_user is not None:
                    connection_label = f'{ssh_user}@{ssh_host}'

                session_group = self[single_section_key].get('group', )
                if session_group is None:
                    session_group = _GROUP_ALL
                else:
                    if session_group in [_GROUP_ALL, _GROUP_LABEL_FOR_ALL, ]:
                        raise AssertionError(session_group, )

                # TODO: Check the section name as it may contain a hostname
                to_return.append(
                    SSHConnectionString(
                        single_section_key,
                        ssh_host,
                        ssh_port,
                        ssh_user,
                        group=session_group,
                        connection_label=connection_label,
                    )
                )
        
        return to_return
    
    @cached_property
    def ssh_sessions_groups(self, ):
        """
        Returns the groups the sessions were linked to

        """
        return list(set([e.group for e in self.ssh_sessions]))

    @cached_property
    def ssh_filename(self, ):
        """
        Returns the absolute path to the ssh executable
        
        """
        return self._ensure_full_path(
            'ssh.executable.filename',
            'ssh.exe',
        )

    @cached_property
    def ssh_add_filename(self):
        """
        Produces the absolute path to the ssh agent

        """
        return self._ensure_full_path(
            'ssh-add.executable.filename',
            'ssh-add.exe',
        )


__all__ = [
    'NativeSSHLauncherConfiguration',
]